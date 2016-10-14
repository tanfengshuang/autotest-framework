import logging, os, commands, re, imp
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils, virt_test_utils
from autotest_lib.client.virt import kvm_vm, virt_env_process


def run_acpi_after_hotplug(test, params, env):
    """
    Test acpi operation after hotplug PCI devices.

    (Elements between [] are configurable test parameters)
    1) PCI add a deivce (NIC / block)
    2) Compare output of monitor command 'info pci'.
    3) reboot/shutdown/s3/s4 guest

    @param test:   KVM test object.
    @param params: Dictionary with the test parameters.
    @param env:    Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)

    test_timeout = int(params.get("test_timeout", 360))

    # Modprobe the module if specified in config file
    module = params.get("modprobe_module")
    if module:
        session.cmd("modprobe %s" % module)

    # Get output of command 'info pci' as reference
    info_pci_ref = vm.monitor.info("pci")


    tested_model = params.get("pci_model")
    test_type = params.get("pci_type")
    image_format = params.get("image_format_stg")

    # Probe qemu to verify what is the supported syntax for PCI hotplug
    if virt_utils.has_option("qmp") and params.get("monitor_type") == "qmp":
        cmd_output = vm.monitor.info("commands")
    else:
        cmd_output = vm.monitor.send_args_cmd("help")
    if len(re.findall("device_add", str(cmd_output))) > 0:
        cmd_type = "device_add"
    elif len(re.findall("pci_add", str(cmd_output))) > 0:
        cmd_type = "pci_add"
    else:
        raise error.TestError("Unknow version of qemu")

    if cmd_type == "pci_add":
        if test_type == "nic":
            pci_add_cmd = "pci_add pci_addr=auto nic model=%s" % tested_model
        elif test_type == "block":
            image_params = virt_utils.get_sub_dict(params, "stg")
            image_filename = kvm_vm.get_image_filename(image_params,
                                                       test.bindir)
            pci_add_cmd = ("pci_add pci_addr=auto storage file=%s,if=%s" %
                           (image_filename, tested_model))
        # Execute pci_add (should be replaced by a proper monitor method call)
        add_output = vm.monitor.send_args_cmd(pci_add_cmd, convert=False)
        if not "OK domain" in add_output:
            raise error.TestFail("Add PCI device failed. "
                                 "Monitor command is: %s, Output: %r" %
                                 (pci_add_cmd, add_output))
        after_add = vm.monitor.info("pci")

    elif cmd_type == "device_add":
        driver_id = test_type + "-" + virt_utils.generate_random_id()
        device_id = test_type + "-" + virt_utils.generate_random_id()
        if test_type == "nic":
            if tested_model == "virtio":
                tested_model = "virtio-net-pci"
            pci_add_cmd = "device_add id=%s,driver=%s" % (device_id, tested_model)
        elif test_type == "block":
            image_params = virt_utils.get_sub_dict(params, "stg")
            image_filename = kvm_vm.get_image_filename(image_params,
                                                       test.bindir)
            if tested_model == "virtio":
                tested_model = "virtio-blk-pci"

            if tested_model == "scsi":
                tested_model = "scsi-disk"

            driver_add_cmd = (" __com.redhat_drive_add "
                              "file=%s,format=%s,id=%s" %
                              (image_filename, image_format, driver_id))
            pci_add_cmd = ("device_add id=%s,driver=%s,drive=%s" %
                           (device_id, tested_model, driver_id))
            driver_output = vm.monitor.send_args_cmd(driver_add_cmd,
                                                              convert=False)
        add_output = vm.monitor.send_args_cmd(pci_add_cmd)
        after_add = vm.monitor.info("pci")
        if device_id not in after_add:
            raise error.TestFail("Add device failed. Monitor command is: %s"
                                 ". Output: %r" % (pci_add_cmd, add_output))

        # Compare the output of 'info pci'
    if after_add == info_pci_ref:
        raise error.TestFail("No new PCI device shown after executing "
                             "monitor command: 'info pci'")

    if params.get("sub_type"):
        virt_test_utils.run_sub_test(test, params, env, params.get("sub_type"))
    session.close()

