import logging, time, commands
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils


def run_eject_media(test, params, env):
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

    def change_cdrom(cmd=None):
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
    orig_img_name = params.get("cdrom_cd1")
    eject_cmd = "eject device=%s" % device_name
    vm.monitor.send_args_cmd(eject_cmd)
    logging.info("Wait until device is ejected")
    time.sleep(10)
    blocks_info = vm.monitor.info("block")
    if orig_img_name in str(blocks_info):
        raise error.TestFail("Fail to eject cdrom %s from guest" % orig_img_name)
    
    new_img_name = params.get("new_img_name")
    change_cmd = "change device=%s,target=%s" % (device_name, new_img_name)
    vm.monitor.send_args_cmd(change_cmd)
    logging.info("Wait until device changed")
    time.sleep(10)
    blocks_info = vm.monitor.info("block")
    if new_img_name not in str(blocks_info):
        raise error.TestFail("Fail to chang cdrom to %s for guest" % new_img_name)
    if qmp_used:
        eject_cmd = "eject device=%s, force=True" % device_name
    else:
        eject_cmd = "eject device=%s" % device_name
    vm.monitor.send_args_cmd(eject_cmd)
    logging.info("Wait until new image is ejected")
    time.sleep(10)

    blocks_info = vm.monitor.info("block")
    if new_img_name in str(blocks_info):
        raise error.TestFail("Fail to eject cdrom %s from guest" % orig_img_name)

    device_name = get_block(key="removable", value=False)
    eject_cmd = "eject device=%s," % device_name
    try:
        output = vm.monitor.send_args_cmd(eject_cmd)
    except Exception, e:
        output = str(e)
    if "is not removable" not in output:
        raise error.TestFail("Could remove non-removable device!")
    session.close()
