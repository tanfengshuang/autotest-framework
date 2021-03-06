import logging, time, os, types
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils, virt_test_utils
import threading


def run_migration(test, params, env):
    """
    KVM migration test:
    1) Get a live VM and clone it.
    2) Verify that the source VM supports migration.  If it does, proceed with
            the test.
    3) Send a migration command to the source VM and wait until it's finished.
    4) Kill off the source VM.
    3) Log into the destination VM after the migration is finished.
    4) Compare the output of a reference command executed on the source with
            the output of the same command on the destination machine.

    @param test: kvm test object.
    @param params: Dictionary with test parameters.
    @param env: Dictionary with the test environment.
    """
    def guest_stress_start(guest_stress_test):
        """
        Start a stress test in guest, Could be 'iozone', 'dd', 'stress'

        @param type: type of stress test.
        """
        from autotest_lib.client.virt.tests import autotest

        timeout = 0

        if guest_stress_test == "autotest":
            test_type = params.get("test_type")
            func = autotest.run_autotest
            new_params = params.copy()
            new_params["test_control_file"] = "%s.control" % test_type

            args = (test, new_params, env)
            timeout = 60
        elif guest_stress_test == "dd":
            vm = env.get_vm(env, params.get("main_vm"))
            vm.verify_alive()
            session = vm.wait_for_login(timeout=login_timeout)
            func = session.cmd_output
            args = ("for((;;)) do dd if=/dev/zero of=/tmp/test bs=5M "
                    "count=100; rm -f /tmp/test; done",
                    login_timeout, logging.info)

        logging.info("Start %s test in guest", guest_stress_test)
        bg = virt_test_utils.BackgroundTest(func, args)
        params["guest_stress_test_pid"] = bg
        bg.start()
        if timeout:
            logging.info("sleep %ds waiting guest test start.", timeout)
            time.sleep(timeout)
        if not bg.is_alive():
            raise error.TestFail("Failed to start guest test!")

    def guest_stress_deamon():
        """
        This deamon will keep watch the status of stress in guest. If the stress
        program is finished before migration this will restart it.
        """
        while True:
            action = params.get("action")
            if action == "run":
                logging.debug("Check if guest stress is still running")
                bg = params.get("guest_stress_test_pid")
                guest_stress_test = params.get("guest_stress_test")
                if bg and not bg.is_alive():
                    logging.debug("Stress process finished, restart it")
                    guest_stress_start(guest_stress_test)
                    time.sleep(30)
                else:
                    logging.debug("Stress still on")
            else:
                bg = params.get("guest_stress_test_pid")
                if bg and bg.is_alive():
                    try:
                        bg.join()
                    except:
                        pass
                break
            time.sleep(10)

    def get_functions(func_names, locals_dict):
        """
        Find sub function(s) in this function with the given name(s).
        """
        if not func_names:
            return []
        funcs = []
        for f in func_names.split():
            f = locals_dict.get(f)
            if isinstance(f, types.FunctionType):
                funcs.append(f)
        return funcs

    def mig_set_speed():
        mig_speed = params.get("mig_speed", "1G")
        return vm.monitor.migrate_set_speed(mig_speed)

    mig_timeout = float(params.get("mig_timeout", "3600"))
    mig_protocol = params.get("migration_protocol", "tcp")
    mig_cancel_delay = int(params.get("mig_cancel") == "yes") * 2
    offline = params.get("offline", "no") == "yes"
    check = params.get("vmstate_check", "no") == "yes"
    living_guest_os = params.get("migration_living_guest", "yes") == "yes"
    deamon_thread = None

    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    if living_guest_os:
        timeout = int(params.get("login_timeout", 360))
        session = vm.wait_for_login(timeout=timeout)

        # Get the output of migration_test_command
        test_command = params.get("migration_test_command")
        reference_output = session.cmd_output(test_command)

        # Start some process in the background (and leave the session open)
        background_command = params.get("migration_bg_command", "")
        session.sendline(background_command)
        time.sleep(5)

        # Start another session with the guest and make sure the background
        # process is running
        session2 = vm.wait_for_login(timeout=timeout)

        try:
            check_command = params.get("migration_bg_check_command", "")
            session2.cmd(check_command, timeout=30)
            session2.close()

            # run some functions before migrate start.
            pre_migrate = get_functions(params.get("pre_migrate"), locals())
            for func in pre_migrate:
                func()

            # Start stress test in guest.
            guest_stress_test = params.get("guest_stress_test")
            if guest_stress_test:
                guest_stress_start(guest_stress_test)
                params["action"] = "run"
                deamon_thread = virt_test_utils.BackgroundTest(guest_stress_deamon, ())
                deamon_thread.start()

            # Migrate the VM
            ping_pong = params.get("ping_pong", 1)
            for i in xrange(int(ping_pong)):
                if i % 2 == 0:
                    logging.info("Round %s ping..." % str(i / 2))
                else:
                    logging.info("Round %s pong..." % str(i / 2))
                vm.migrate(mig_timeout, mig_protocol, mig_cancel_delay,
                           offline, check)

            # Set deamon thread action to stop after migrate
            params["action"] = "stop"

            # run some functions after migrate finish.
            post_migrate = get_functions(params.get("post_migrate"), locals())
            for func in post_migrate:
                func()

            # Log into the guest again
            logging.info("Logging into guest after migration...")
            session2 = vm.wait_for_login(timeout=30)
            logging.info("Logged in after migration")

            # Make sure the background process is still running
            session2.cmd(check_command, timeout=30)

            # Get the output of migration_test_command
            output = session2.cmd_output(test_command)

            # Compare output to reference output
            if output != reference_output:
                logging.info("Command output before migration differs from "
                             "command output after migration")
                logging.info("Command: %s", test_command)
                logging.info("Output before:" +
                             virt_utils.format_str_for_message(reference_output))
                logging.info("Output after:" +
                             virt_utils.format_str_for_message(output))
                raise error.TestFail("Command '%s' produced different output "
                                 "before and after migration" % test_command)

        finally:
            # Kill the background process
            if session2 and session2.is_alive():
                session2.cmd_output(params.get("migration_bg_kill_command", ""))
            if deamon_thread is not None:
                deamon_thread.join()

        session2.close()
        session.close()
    else:
        # Just migrate without depending on a living guest OS
        vm.migrate(mig_timeout, mig_protocol, mig_cancel_delay, offline, check)
