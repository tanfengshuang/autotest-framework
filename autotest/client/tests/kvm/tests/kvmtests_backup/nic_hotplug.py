import logging, os, commands, re, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_test_utils, virt_utils


def run_nic_hotplug(test, params, env):
    """
    Test hotplug of NIC devices

    1) Boot up guest with one nic
    2) Add a host network device through monitor cmd and check if it's added
    3) Add nic device through monitor cmd and check if it's added
    4) Check if new interface gets ip address
    5) Disable primary link of guest
    6) Ping guest new ip from host
    7) Delete nic device and netdev
    8) Re-enable primary link of guest

    @param test:   KVM test object.
    @param params: Dictionary with the test parameters.
    @param env:    Dictionary with test environment.
    """

    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    guest_delay = int(params.get("guest_delay", 20))
    session = vm.wait_for_login(timeout=timeout)
    romfile = params.get("romfile")

    # Modprobe the module if specified in config file
    module = params.get("modprobe_module")
    if module:
        session.get_command_output("modprobe %s" % module)

    def netdev_add(vm):
        netdev_id = virt_utils.generate_random_id()
        attach_cmd = ("netdev_add type=tap,id=%s" % netdev_id)
        nic_script = params.get("nic_script")
        if nic_script:
            attach_cmd += ",script=%s" % virt_utils.get_path(vm.root_dir,
                                                            nic_script)
        netdev_extra_params = params.get("netdev_extra_params")
        if netdev_extra_params:
            attach_cmd += ",%s" % netdev_extra_params
        logging.info("Adding netdev through %s" % attach_cmd)
        vm.monitor.send_args_cmd(attach_cmd, convert=False)

        network = vm.monitor.info("network")
        if netdev_id not in network:
            logging.error(network)
            raise error.TestError("Fail to add netdev: %s" % netdev_id)
        else:
            return netdev_id

    def netdev_del(vm, n_id):
        vm.monitor.cmd("netdev_del %s" % n_id)

        network = vm.monitor.info("network")
        if n_id in network:
            logging.error(network)
            raise error.TestError("Fail to remove netdev %s" % n_id)

    def nic_add(vm, model, netdev_id, mac, rom=None):
        """
        Add a nic to virtual machine

        @vm: VM object
        @model: nic model
        @netdev_id: id of netdev
        @mac: Mac address of new nic
        @rom: Rom file
        """
        nic_id = virt_utils.generate_random_id()
        if model=="virtio": model="virtio-net-pci"
        device_add_cmd = "device_add driver=%s,netdev=%s,mac=%s,id=%s" % (model,
                                                                   netdev_id,
                                                                   mac, nic_id)
        if rom:
            device_add_cmd += ",romfile=%s" % rom
        logging.info("Adding nic through %s" % device_add_cmd)
        vm.monitor.send_args_cmd(device_add_cmd, convert=False)

        qdev = vm.monitor.info("qtree")
        if not nic_id in qdev:
            logging.error(qdev)
            raise error.TestFail("Device %s was not plugged into qdev"
                                 "tree" % nic_id)
        else:
            return nic_id

    def nic_del(vm, nic_id, wait=True):
        """
        Remove the nic from pci tree.

        @vm: VM object
        @id: the nic id
        @wait: Whether need to wait for the guest to unplug the device
        """
        nic_del_cmd = "device_del id=%s" % nic_id
        vm.monitor.send_args_cmd(nic_del_cmd)
        if wait:
            logging.info("waiting for the guest to finish the unplug")
            if not virt_utils.wait_for(lambda: nic_id not in
                                      vm.monitor.info("qtree"),
                                      guest_delay, 5 ,1):
                logging.error(vm.monitor.info("qtree"))
                raise error.TestError("Device is not unplugged by "
                                      "guest, please check whether the "
                                      "hotplug module was loaded in guest")

    logging.info("Attach a virtio nic to vm")
    mac = virt_utils.generate_mac_address(vm.instance, 1)
    if not mac:
        mac = "00:00:02:00:00:02"
    netdev_id = netdev_add(vm)
    device_id = nic_add(vm, "virtio", netdev_id, mac, romfile)

    if "Win" not in params.get("guest_name", ""):
        session.sendline("killall dhclient && dhclient %s &" %
                         virt_test_utils.get_linux_ifname(session, mac))

    logging.info("Shutting down the primary link")
    vm.monitor.set_link(vm.netdev_id[0], 'off')

    try:
        logging.info("Waiting for new nic's ip address acquisition...")
        if not virt_utils.wait_for(lambda: (vm.address_cache.get(mac) is
                                           not None), 10, 1):
            raise error.TestFail("Could not get ip address of new nic")
        ip = vm.address_cache.get(mac)
        if not virt_utils.verify_ip_address_ownership(ip, mac):
            raise error.TestFail("Could not verify the ip address of new nic")
        else:
            logging.info("Got the ip address of new nic: %s" % ip)

        logging.info("Ping test the new nic ...")
        s, o = virt_test_utils.ping(ip, 10, timeout=15)
        if s != 0:
            logging.error(o)
            raise error.TestFail("New nic failed ping test")
        vm.monitor.cmd("stop")
        vm.monitor.cmd("cont")
        s, o = virt_test_utils.ping(ip, 10, timeout=15)
        if s != 0:
            logging.error(o)
            raise error.TestFail("New nic failed ping test after stop/cont")

        logging.info("Detaching a virtio nic from vm")
        nic_del(vm, device_id)
        netdev_del(vm,netdev_id)

    finally:
        vm.free_mac_address(1)
        logging.info("Re-enabling the primary link")
        vm.monitor.set_link(vm.netdev_id[0], 'on')
