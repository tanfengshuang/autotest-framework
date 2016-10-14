import logging, time
import threading
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_test_utils, virt_utils


def run_migration_after_nichotplug(test, params, env):
    """
    KVM migration test:
    1) Get a live VM and clone it.
    2) Verify that the source VM supports migration.  If it does, proceed with
       the test.
    3) Hotplug a nic.
    4) Send a migration command to the source VM and wait until it's finished.
    5) Kill off the source VM.
    6) Log into the destination VM after the migration is finished.

    @param test: kvm test object.
    @param params: Dictionary with test parameters.
    @param env: Dictionary with the test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session_serial = vm.wait_for_serial_login(timeout=timeout)
    # Modprobe the module if specified in config file
    module = params.get("modprobe_module")
    if module:
        session_serial.cmd_output("modprobe %s" % module)

    mig_timeout = float(params.get("mig_timeout", "3600"))
    mig_protocol = params.get("migration_protocol", "tcp")
    mig_cancel = bool(params.get("mig_cancel"))

    def netdev_add(vm):
        netdev_id = virt_utils.generate_random_id()
        netdev_string = ("tap,id=%s,script=%s" %
                        (netdev_id, virt_utils.get_path(vm.root_dir,
                                                   params.get("nic_script"))))
        attach_cmd = "netdev_add " + netdev_string
        netdev_extra_params = params.get("netdev_extra_params")
        if netdev_extra_params:
            attach_cmd += ",%s" % netdev_extra_params
        logging.info("Adding netdev through %s", attach_cmd)
        vm.monitor.cmd(attach_cmd)

        network = vm.monitor.info("network")
        if netdev_id not in network:
            logging.error(network)
            raise error.TestError("Fail to add netdev: %s" % netdev_id)
        else:
            return (netdev_id, netdev_string)

    def nic_add(vm, model, netdev_id, mac):
        """
        Add a nic to virtual machine

        @vm: VM object
        @model: nic model
        @netdev_id: id of netdev
        @mac: Mac address of new nic
        """
        nic_id = virt_utils.generate_random_id()
        if model == "virtio":
            model = "virtio-net-pci"

        device_string = "%s,netdev=%s,mac=%s,id=%s" % (model,
                                                       netdev_id,
                                                       mac, nic_id)
        device_add_cmd = "device_add " + device_string
        logging.info("Adding nic through %s", device_add_cmd)
        vm.monitor.cmd(device_add_cmd)

        qdev = vm.monitor.info("qtree")
        if nic_id not in qdev:
            logging.error(qdev)
            raise error.TestFail("Device %s was not plugged into qdev"
                                 "tree" % nic_id)
        else:
            return (nic_id, device_string)

    nic_model = params.get("nic_model")
    logging.info("Attach a %s nic to vm" % nic_model)
    mac = virt_utils.generate_mac_address(vm.instance, 1)
    if not mac:
        mac = "00:00:02:00:00:02"
    (netdev_id, netdev_string) = netdev_add(vm)
    (device_id, device_string) = nic_add(vm, nic_model, netdev_id, mac)

    if "Win" not in params.get("guest_name", ""):
        session_serial.sendline("dhclient %s &" %
        virt_test_utils.get_linux_ifname(session_serial, mac))

    logging.info("Shutting down the primary link")
    vm.monitor.cmd("set_link %s down" % vm.netdev_id[0])

    try:
        logging.info("Waiting for new nic's ip address acquisition...")
        if not virt_utils.wait_for(lambda: (vm.address_cache.get(mac) is
                                           not None), 10, 1):
            raise error.TestFail("Could not get ip address of new nic")
        ip = vm.address_cache.get(mac)
        if not virt_utils.verify_ip_address_ownership(ip, mac):
            raise error.TestFail("Could not verify ip address of new nic")
        else:
            logging.info("Got the ip address of new nic: %s", ip)

        logging.info("Ping test the new nic ...")
        s, o = virt_test_utils.ping(ip, 100)
        if s != 0:
            logging.error(o)
            raise error.TestFail("New nic failed ping test")

        logging.info("Re-enabling the primary link")
        vm.monitor.cmd("set_link %s up" % vm.netdev_id[0])

        vm.params['extra_params'] += " -device %s -netdev %s" % (device_string,
                                                                 netdev_string)
        vm = virt_test_utils.migrate(vm, env, mig_timeout, mig_protocol, False)

        logging.info("Shutting down the primary link")
        vm.monitor.cmd("set_link %s down" % vm.netdev_id[0])
        logging.info("Ping test the new nic ...")
        s, o = virt_test_utils.ping(ip, 100)
        if s != 0:
            logging.error(o)
            raise error.TestFail("New nic failed ping test")

        logging.info("Re-enabling the primary link")
        vm.monitor.cmd("set_link %s up" % vm.netdev_id[0])
    finally:
        vm.free_mac_address(1)
        session_serial.close()
