import logging, time, string
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import kvm_monitor


def run_balloon_disable(test, params, env):
    """
    KVM balloon disable test:
    1) Log into a guest
    2) Send a system monitor command (info balloon) and check return value

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login(timeout=float(params.get("login_timeout", 240)))
    try:
        output =  vm.monitor.info("balloon")
    except kvm_monitor.QMPCmdError, e:
        output = str(e)
    if "has not been activated" not in output:
        raise error.TestFail("Balloon driver still on when disable"
                            " it on command line")
    session.close()
