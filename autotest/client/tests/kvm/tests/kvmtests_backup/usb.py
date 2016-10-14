import logging
from autotest_lib.client.common_lib import error
import kvm_test_utils

def run_usb(test, params, env):
    """
    Test usb device of guest

    1) create a image file by qemu-img
    2) boot up a guest add this file as a usb device
    3) check usb device information by execute monitor/guest command

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    output = vm.monitor.cmd("info usb")
    if "Product QEMU USB MSD" not in output:
        logging.debug(output)
        raise error.TestFail("Could not find mass storage device")
    output = session.get_command_output("lsusb")
    #no bus specified, default using "usb.0" for "usb-storage"
    if "ID 0000:0000" not in output:
        logging.debug(output)
        raise error.TestFail("No 'ID 0000:0000' in the output of 'lsusb'")
    output = session.get_command_output("fdisk -l")
    if params.get("fdisk_string") not in output:
        logging.debug(output)
        raise error.TestFail("Could not realise the usb device")
    dev_list = session.get_command_output("ls /dev/sd[a-z]")
    if session.get_command_status("yes |mkfs %s" % dev_list.split()[-1],
                               timeout=int(params.get("format_timeout"))) != 0:
        raise error.TestFail("Could not format usb disk")
    output = session.get_command_output("dmesg")
    if "Buffer I/O error" in output:
        logging.debug(output)
        raise error.TestFail("Exists I/O error when format usb device")
    session.close()
