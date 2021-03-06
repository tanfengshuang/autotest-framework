import logging, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_test_utils, virt_utils


def run_change_media(test, params, env):
    """
    change a removable media:
    1) Boot VM with QMP/human monitor enabled.
    2) Connect to QMP/human monitor server.
    3) Check current block information.
    4) Insert some file to cdrom.
    5) Check current block information again.
    6) Mount cdrom to /mnt in guest to make it locked.
    7) Check current block information to make sure cdrom is locked.
    8) Change cdrom without force.
    9) Change cdrom with force. (qmp only)
    10) Change a non-removable media.

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environmen.
    """

    def check_block_locked(block_name):
        blocks_info = vm.monitor.info("block")

        if type(blocks_info) == type(""):
            lock_str = "locked=1"
            for block in blocks_info.splitlines():
                if block_name in block and lock_str in block:
                    return True
        else:
            for block in blocks_info:
                if block['device'] == block_name and block['locked']:
                    return True
        return False

    def change_block(cmd=None):
        try:
            output = vm.monitor.send_args_cmd(cmd)
        except Exception, e:
            output = str(e)
        return output

    def get_block(key="type", value="cdrom"):
        blocks_info = vm.monitor.info("block")
        if type(blocks_info) == type(""):
           if value == True:
               check_str = "%s=1" % key
           elif value == False:
               check_str = "%s=0" % key
           else:
               check_str = "%s=%s" % (key, value)
           for block in blocks_info.splitlines():
               if check_str in block:
                   return block.split(":")[0]
        else:
            for block in blocks_info:
                if block[key] == value:
                   return block['device']



    if not virt_utils.has_option("qmp"):
        logging.warn("qemu does not support qmp. Human monitor will be used.")
    qmp_used = False
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    logging.info("Wait until device is ready")
    time.sleep(10)

    blocks_info = vm.monitor.info("block")
    if type(blocks_info) == type({}):
        qmp_used = True

    device_name = get_block(key="type", value="cdrom")
    orig_img_name = params.get("orig_img_name")
    change_insert_cmd = "change device=%s,target=%s" % (device_name,
                                                            orig_img_name)
    vm.monitor.send_args_cmd(change_insert_cmd)
    logging.info("Wait until device is ready")
    time.sleep(10)
    blocks_info = vm.monitor.info("block")
    if orig_img_name not in str(blocks_info):
        raise error.TestFail("Fail to insert device %s to guest" % orig_img_name)

    if check_block_locked(device_name):
        raise error.TestFail("device is locked by default.")

    cdrom = virt_test_utils.get_readable_cdroms(params, session)[0]
    mount_cmd = params.get("cd_mount_cmd") % cdrom
    (s, o) = session.cmd_status_output(mount_cmd, timeout=360)
    if s:
        raise error.TestError("Fail command: %s\nOutput: %s" % (mount_cmd, o))

    if not check_block_locked(device_name):
        raise error.TestFail("device is not locked after mount it in guest.")


    new_img_name = params.get("new_img_name")
    change_insert_cmd = "change device=%s,target=%s" % (device_name,
                                                                new_img_name)
    output = change_block(change_insert_cmd)
    if "is locked" not in output:
        raise error.TestFail("Device is not locked")

    if qmp_used:
        change_insert_cmd = "change device=%s,target=%s,force=True" %\
                                               (device_name, new_img_name)
        output = change_block(change_insert_cmd)
        if "is locked" not in output:
            raise error.TestFail("Device is not locked")

    blocks_info = vm.monitor.info("block")
    if orig_img_name not in str(blocks_info):
        raise error.TestFail("Locked device %s is changed!" % orig_img_name)

    device_name = get_block(key="removable", value=False)
    change_insert_cmd = "change device=%s,target=%s" % (device_name,
                                                                new_img_name)
    output = change_block(change_insert_cmd)
    if "is not removable" not in output:
        raise error.TestFail("Could remove non-removable device!")
    session.close()
