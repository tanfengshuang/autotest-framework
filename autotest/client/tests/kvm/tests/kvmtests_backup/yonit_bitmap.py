import logging, time, random, signal
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils
from autotest_lib.client.virt.tests import guest_test


def run_yonit_bitmap(test, params, env):
    """
    Run yonit bitmap benchmark in Windows guests, especially win7 32bit,
    for regression test of BZ #556455.

    Run the benchmark (infinite) loop background using
    run_guest_test_background, and detect the existance of the process
    in guest.

      1. If the process exits before test timeout, that means the benchmark
      exits unexpectly, and BSOD may have happened, which can be verified
      from the screenshot saved by kvm-autotest framework.
      2. If just timeout happen, this test passes, i.e. the guest stays
      good while running the benchmark in the given time.

    @param test: Kvm test object
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """

    sec_per_day = 86400 # seconds per day
    test_timeout = int(params.get("test_timeout", sec_per_day))
    login_timeout = int(params.get("login_timeout", 360))

    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    session = vm.wait_for_login(timeout=login_timeout)

    # Since the benchmark runs into an infinite loop, the background process
    # will never return, unless we got BSOD.
    #
    # We set the test_timeout of the background guest_test much bigger than
    # that of this test to make sure that the background benchmark is still
    # running while the the foreground detecting is on going.
    params["test_timeout"] = test_timeout * 2 + sec_per_day
    pid = guest_test.run_guest_test_background(test, params, env,
                                                     "yonit_bitmap_benchmark")
    if pid < 0:
        session.close()
        raise error.TestError("Could not create child process to execute "
                              "guest_test background")


    def is_yonit_benchmark_launched():
        if session.get_command_status(
            'tasklist | find /I "compress_benchmark_loop"') != 0:
            logging.debug("yonit bitmap benchmark is not found")
            return False
        return True


    try:
        # Start detecting whether the benchmark is started a few mins
        # after the background test launched, as the downloading
        # will take some time.
        launch_timeout = login_timeout
        if virt_utils.wait_for(is_yonit_benchmark_launched,
                              launch_timeout, 180, 5):
            logging.debug("Yonit bitmap benchmark is launched successfully")
        else:
            raise error.TestError("Failed to launch yonit bitmap benchmark")

        # If the benchmark exits before timeout, errors happened.
        if virt_utils.wait_for(lambda: not is_yonit_benchmark_launched(),
                              test_timeout, 60, 10):
            raise error.TestError("Yonit bitmap benchmark exits unexpectly")
        else:
            if session.is_responsive():
                logging.info("SUCCEED. Guest stays good until test timeout")
            else:
                raise error.TestFail("Guest is dead")
    finally:
        logging.info("Kill the background benchmark tracking process")
        virt_utils.safe_kill(pid, signal.SIGKILL)
        guest_test.wait_guest_test_background(pid)
        session.close()
