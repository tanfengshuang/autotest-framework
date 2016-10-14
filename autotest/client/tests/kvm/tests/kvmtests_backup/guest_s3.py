import logging, time
from autotest_lib.client.common_lib import error


def run_guest_s3(test, params, env):

    """
    Suspend a guest os to memory.
    Support both Linux and Windows guest.

    Recommend using Linux+VNC / Windows+SPICE

    This test do the following steps:
    1) boot a guest.
    2) clear guest's log and check(Linux guest) or enable(Windows guest) S3 mode
         if dont support,error this test.
    3) run a background program as a flag ,and push guest into S3 state.
    4) sleep a while for guest resume.
    5) check weather background program still running, if not ,error this test.
    6) check guest system_log,if not acpi s3 message found,fail this test.

    Something need to notice:
    Because WinXP/2003 didnt record ACPI event into log,
        so will always pass this test if the guest's driver supports S3

    @param test: kvm test object.
    @param params: Dictionary with test parameters.
    @param env: Dictionary with the test environment.

    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    login_timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=login_timeout)

    logging.info("clear system_log AND checking vm s3 support status")
    session.cmd(params.get("check_s3_support_cmd"))

    try:
        logging.info("run a program in background as a flag")
        session.sendline(params.get("bg_cmd"))

        session2 = vm.wait_for_login(timeout=login_timeout)
        logging.info("putting guest into s3 state")
        session2.cmd(params.get("set_s3_cmd"))

        #Due to WinXP/2003 will not S3 immediately after issue a S3 cmd,
        #    will delay 10~60 secs,maybe there's a bug in windows,I'm still
        #    investigating it.
        time.sleep(60)
        logging.info("sleep 60 seconds for guest resume.")

        if not vm.is_alive():
            raise error.TestFail("VM is dead, Test Failed.")

        bg_status = session2.cmd_status(params.get("check_bg_cmd"))
        s3_status = session2.cmd_status(params.get("check_s3_cmd"))
        logging.debug ("bg_status %s" % bg_status)
        logging.debug ("s3_status %s" % s3_status)

        if bg_status:
            raise error.TestError("backgrond program disappeared after resume.")
        elif s3_status:
            raise error.TestError("Not suspend log found !")
        else:
            logging.info("The system has resumed")

    finally:
        logging.info("remove flag from guest")
        session2.sendline(params.get("kill_bg_cmd"))
        session2.close()
        session.close()
