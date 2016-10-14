import time, logging
from autotest_lib.client.common_lib import error


def run_nmi_watchdog(test, params, env):
    """
    Test the function of nmi injection and verify the response of guest

    1) Log in the guest
    2) Add 'watchdog=1' to boot option
    2) Check if guest's NMI counter augment after injecting nmi

    @param test: kvm test object
    @param params: Dictionary with the test parameters.
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout=int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)
    get_nmi_cmd= params.get("get_nmi_cmd")
    kernel_version = session.get_command_output("uname -r").strip()
    nmi_watchdog_type = int(params.get("nmi_watchdog_type"))
    update_kernel_cmd = "grubby --update-kernel=/boot/vmlinuz-%s " \
     "--args='nmi_watchdog=%d'"  % (kernel_version, nmi_watchdog_type)

    logging.info("Add 'nmi_watchdog=%d' to guest kernel cmdline and reboot"
                 % nmi_watchdog_type)
    if session.get_command_status(update_kernel_cmd) != 0:
        raise error.TestError("Fail to modify the kernel cmdline")
    time.sleep(int(params.get("sleep_before_reset", 10)))
    session = vm.reboot(session, method='shell', timeout=timeout)
    try:
        s, guest_cpu_num = session.get_command_status_output(
                                                  params.get("cpu_chk_cmd"))
        if s != 0:
            raise error.TestError("Fail to get cpu number of guest")

        logging.info("Checking the nmi interrupt")
        s, o = session.get_command_status_output(get_nmi_cmd)
        if s != 0:
            raise error.TestError("Fail to get guest's NMI counter")
        nmi_counter1 = o.split()[1:]

        time.sleep(60)
        s, o = session.get_command_status_output(get_nmi_cmd)
        if s != 0:
            raise error.TestError("Fail to get guest's NMI counter")
        nmi_counter2 = o.split()[1:]

        for i in range(int(guest_cpu_num)):
            logging.info("vcpu: %s, nmi_counter1: %s, nmi_counter2: %s" %
                         (i, nmi_counter1[i], nmi_counter2[i]))
            if int(nmi_counter2[i]) <= int(nmi_counter1[i]):
                raise error.TestFail("The counter doesn't increase")
    finally:
        session.close()
