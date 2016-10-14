import logging, re, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils
from autotest_lib.client.virt import virt_test_utils

def run_cdrom(test, params, env):
    """
    KVM cdrom test:
    1) Boot up a VM with one iso
    2) Check if VM identify iso file
    3) Eject cdrom and change with another iso for many times
    4) Try to fromat cdrom and check the return string
    5) Mount cdrom device to /mnt
    6) Copy file from cdrom and compare files by diff
    7) Umount and mount many times

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    def get_cdrom_info():
        o = vm.monitor.info("block")
        if isinstance(o, str):
            try:
                device = re.findall("(.*ide.*):.*tray-open.*", o)[0]
            except IndexError:
                device = None
            try:
                file = re.findall("%s: .*file=(\S*) " % device, o)[0]
            except IndexError:
                file = None
        elif isinstance(o, list):
            for block in o:
                 if 'tray-open' in block.keys() and 'ide' in block['device']:
                     device = block['device']
                     try:
                         file = block['inserted']['file']
                     except KeyError:
                         file = None
        logging.debug("Device name: %s, ISO: %s" % (device, file))
        return (device, file)

    def check_cdrom_locked(cdrom):
        blocks_info = vm.monitor.info("block")
        if isinstance(blocks_info, str):
            lock_str = "locked=1"
            for block in blocks_info.splitlines():
                if cdrom in block and lock_str in block:
                    return True
        else:
            for block in blocks_info:
                if 'inserted' in block.keys() and\
                       block['inserted']['file'] == cdrom:
                    return block['locked']
        return False


    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))
    cdrom_orig = params.get("cdrom_cd1")
    cdrom_new = params.get("new_iso")
    cdrom = cdrom_orig

    cdrom_dev = virt_test_utils.get_readable_cdroms(params, session)[0]

    logging.info("Detecting the existence of cdrom")
    (device, file) = get_cdrom_info()
    if file != cdrom:
        raise error.TestError("%s does not realized" % cdrom)

    session.get_command_output("umount %s" % cdrom_dev)
    if not virt_utils.wait_for(lambda: not check_cdrom_locked(file), 300):
        raise error.TestError("%s could not become unlocked" % device)

    max_times = int(params.get("max_times", 100))
    logging.info("Eject the cdrom for %s times" % max_times)
    max = max_times
    while max > 0:
        vm.monitor.send_args_cmd("eject device=%s" % device)
        (device, file) = get_cdrom_info()
        if file is not None:
            raise error.TestFail("%s is not ejected" % cdrom)

        cdrom = cdrom_new
        if max % 2 == 0:
            cdrom = cdrom_orig
        vm.monitor.send_args_cmd("change device=%s, target=%s" % (device, cdrom))
        time.sleep(10)
        (device, file) = get_cdrom_info()
        if file != cdrom:
            raise error.TestError("%s is not changed" % cdrom)
        max -= 1

    logging.info("Check whether the cdrom is read-only")
    filename = params.get("filename")
    dest_dir = "/mnt"
    s, o = session.get_command_status_output("echo y|mkfs %s" % cdrom_dev)
    if not "Read-only" in o:
        logging.debug("Format cdrom doesn't return Read-only error")
    if s == 0:
        raise error.TestFail("Format %s unexpected success" % cdrom_dev)

    if not virt_utils.wait_for(lambda: session.get_command_status("mount %s %s"
                                            % (cdrom_dev, dest_dir)) == 0, 30):
        logging.debug(session.get_command_output("cat /etc/mtab"))
        raise error.TestFail("Could not mount %s" % cdrom_dev)

    logging.info("File copying test")
    cmd = "/bin/cp -f %s/%s /tmp"
    if session.get_command_status(cmd % (dest_dir, filename)) != 0:
        raise error.TestFail("Fail to copy file from %s" % dest_dir)
    cmd = "diff %s/%s /tmp/%s" % (dest_dir, filename, filename)
    if session.get_command_status(cmd) != 0:
        raise error.TestFail("Two file is different, cmd: %s" % cmd)

    logging.info("Mounting/Unmounting test")
    max = max_times
    while max > 0:
        if session.get_command_status("umount %s" % cdrom_dev) != 0:
            raise error.TestFail("Could not umount %s" % cdrom_dev)
        cmd = "mount %s %s" % (cdrom_dev, dest_dir)
        if session.get_command_status(cmd) != 0:
            logging.debug(session.get_command_output("cat /etc/mtab"))
            raise error.TestFail("Could not mount %s" % cdrom_dev)
        max -= 1

    session.close()
