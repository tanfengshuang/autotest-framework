import logging
from autotest_lib.client.common_lib import error

def run_fillup_disk(test, params, env):
    """
    Fillup guest disk (root mount point) using dd if=/dev/zero,
    and then clean up (rm the big file). The main purpose of this case is to
    expand the qcow2 file to its max size.

    Suggest to test rebooting vm after this test.

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    fillup_timeout = int(params.get("fillup_timeout"))
    fillup_size = int(params.get("fillup_size"))
    fill_dir = params.get("guest_testdir","/")
    filled = False
    number = 0

    try:
        logging.info("Start filling the disk in %s" % fill_dir)
        while not filled:
            # As we want to test the backing file, so bypass the cache
            cmd = params.get("fillup_cmd")
            logging.debug(cmd)
            s, o = session.get_command_status_output( \
                cmd % (fill_dir, number, fillup_size), timeout=fillup_timeout)
            if "No space left on device" in o:
                logging.debug("Successfully fill up the disk")
                filled = True;
            elif s != 0:
                logging.error(o)
                raise error.TestFail("Unexpected results got from dd command")
            number += 1
    finally:
        logging.info("Cleaning the temporary files...")
        while number >= 0:
            cmd = "rm -f /%s/fillup.%d" % (fill_dir, number)
            logging.debug(cmd)
            s, o = session.get_command_status_output(cmd)
            if s != 0:
                logging.error(o)
                raise error.TestFail("Failed to remove file %s: %s;"
                                     "guest may be unresponsive or "
                                     "command timeout" % (number, o))
            number -= 1
        session.close()

    logging.info("Test finish successfully")
