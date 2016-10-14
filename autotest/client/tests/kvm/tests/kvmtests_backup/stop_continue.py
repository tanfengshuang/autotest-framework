import logging
from autotest_lib.client.common_lib import error


def run_stop_continue(test, params, env):
    """
    Suspend a running Virtual Machine and verify its state.
    1) Boot the vm
    2) Suspend the vm through stop command
    3) Verify the state through info status command
    4) Check is the ssh session to guest is still responsive,
       if succeed, fail the test.

    @param test: Kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    login_timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=login_timeout)

    try:
        logging.info("Suspend the virtual machine")
        vm.monitor.cmd("stop")

        logging.info("Verifying the status of virtual machine through monitor")
        o = vm.monitor.info("status")
        if 'paused' not in o and ( "u'running': False" not in str(o)):
            logging.error(o)
            raise error.TestFail("Fail to suspend through monitor command line")

        logging.info("Check the session responsiveness")
        if session.is_responsive():
            raise error.TestFail("Session is still responsive after stop")

        logging.info("Try to resume the guest")
        vm.monitor.cmd("cont")

        o = vm.monitor.info("status")
        m_type = params.get("monitor_type", "human")
        if ('human' in m_type and 'running' not in o) or\
           ('qmp' in m_type and "u'running': True" not in str(o)):
            logging.error(o)
            raise error.TestFail("Could not continue the execution")

        logging.info("Try to re-log into guest")
        session2 = vm.wait_for_login(timeout=login_timeout)

    finally:
        session2.close()
        session.close()
