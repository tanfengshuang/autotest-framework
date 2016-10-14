import logging, time
from autotest_lib.client.common_lib import error


def run_system_reset_bootable(test, params, env):
    """
    KVM reset test:
    1) Boot guest.
    2) Send some times system_reset monitor command.
    3) Log into the guest to verify it could normally boot.

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    reset_times = int(params.get("reset_times",20))
    interval = int(params.get("reset_interval",10))
    wait_time = int(params.get("wait_time_for_reset",60))
    time.sleep(wait_time)

    for i in range(reset_times):
        vm.monitor.cmd("system_reset")
        time.sleep(interval)

    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))
