import logging, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.common_lib import utils
from autotest_lib.client.tests.kvm import kvm_cross_host_utils
from autotest_lib.client.virt import virt_utils, virt_test_utils


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
    def get_functions(func_names, locals_dict):
        if not func_names:
            return []
        funcs = []
        for f in func_names.split():
            f = locals_dict.get(f)
            if isinstance(f, type(lambda:1)):
                funcs.append(f)
        return funcs

    def guest_stress_start(guest_stress_test):
        """
        Start a stress test in guest, Could be 'iozone', 'dd', 'stress'

        @param type: type of stress test.
        """
        from autotest_lib.client.virt.tests import autotest

        timeout = 0

        if guest_stress_test == "iozone":
            func = autotest.run_autotest
            new_params = params.copy()
            new_params["test_control_file"] = "iozone.control"
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
        else:
            func = autotest.run_autotest
            new_params = params.copy()
            new_params["test_control_file"] = "stress.control"
            args = (test, new_params, env)
            timeout = 60

        logging.info("Start %s test in guest", guest_stress_test)
        bg = virt_test_utils.BackgroundTest(func, args)
        params["guest_stress_test"] = bg
        bg.start()
        if timeout:
            logging.info("sleep %ds waiting guest test start.", timeout)
            time.sleep(timeout)
        if not bg.is_alive():
            raise error.TestFail("Failed to start guest test!")

    def guest_stress_stop():
        logging.info("Trying to stop guest stress test.")
        bg = params.get("guest_stress_test")
        if bg and bg.is_alive():
            try:
                bg.join()
            except:
                pass

    def mig_set_downtime():
        mig_downtime = params.get("mig_downtime", "1s")
        return vm.monitor.cmd("migrate_set_downtime %s" % mig_downtime)

    def mig_cancel():
        return vm.monitor.cmd("migrate_cancel")

    def mig_set_speed():
        mig_speed = params.get("mig_speed", "1G")
        return vm.monitor.migrate_set_speed(mig_speed)

    def guest_stop():
        return vm.monitor.cmd("stop")

    def guest_continue():
        return vm.monitor.cmd("cont")

    def guest_reboot():
        sess = vm.wait_for_login(timeout=timeout)
        sess.cmd(params.get("reboot_command"))
        sess.close()

    def guest_boot():
        from autotest_lib.client.virt import virt_env_process
        # start vm after we mount images via nfs.
        params["start_vm"] = "yes"
        virt_env_process.preprocess_vm(test, params, env,
                                        params.get("main_vm"))

    def bg_file_transfer_start():
        #FIXME: now this fucntion support linux guest only, need to
        # add windows guest support.
        def do_scp(addr):
            logging.info("scp to %s", addr)
            while not params.get("stop_bg_file_transfer"):
                virt_utils.scp_to_remote(addr, "22", "root", "redhat",
                                        "/tmp/a.out", "/tmp/a.out")
        cmd = "dd if=/dev/zero of=/tmp/a.out bs=10M count=400"
        utils.system(cmd)
        addr = vm.get_address()
        bg = virt_test_utils.BackgroundTest(do_scp, [addr])
        params["bg_file_transfer"] = bg
        bg.start()

    def bg_file_transfer_stop():
        params["stop_bg_file_transfer"] = True
        bg = params.get("bg_file_transfer")
        if bg and bg.is_alive():
            try: bg.join()
            except: pass

    login_timeout = float(params.get("login_timeout", "3600"))
    timeout = int(params.get("login_timeout", 360))

    remote_host, xmlrpc_server = kvm_cross_host_utils.test_init(test,
                                                            params, env)
    if params.get("slaver_peer") == "yes":
        # on remote_host, do noting except start a xmlrpc_server.
        logging.info("waiting server thread finish.")
        virt_utils.wait_for(lambda: not xmlrpc_server.is_alive(),
                           login_timeout)
        # finish test on slaver peer.
        kvm_cross_host_utils.test_finish(remote_host, xmlrpc_server,
                                         login_timeout)
        return


    mig_timeout = float(params.get("mig_timeout", "3600"))
    mig_protocol = params.get("migration_protocol", "tcp")

    vm = env.get_vm(params["main_vm"])
    session = None
    test_command = params.get("migration_test_command")
    reference_output = None
    session2 = None

    if params.get("start_vm") == "yes":
        vm = env.get_vm(params["main_vm"])
        vm.verify_alive()
        session = vm.wait_for_login(timeout=login_timeout)
        # Get the output of migration_test_command
        reference_output = session.cmd_output(test_command)

        # Start some process in the background (and leave the session open)
        background_command = params.get("migration_bg_command", "")
        session.sendline(background_command)
        time.sleep(5)

        # Start another session with the guest and make sure the background
        # process is running
        session2 = vm.wait_for_login(timeout=timeout)

    try:
        check_command = params.get("migration_bg_check_command", '')
        if session2 and (check_command is not ''):
            session2.cmd(check_command, timeout=30)
            session2.close()

        # start stress test in guest.
        guest_stress_test = params.get("guest_stress_test")
        if guest_stress_test:
            guest_stress_start(guest_stress_test)

        # run some functions before migrate start.
        pre_migrate = get_functions(params.get("pre_migrate"), locals())
        for func in pre_migrate:
            func()

        # Migrate the VM
        during_migrate = get_functions(params.get("during_migrate"), locals())
        dest_vm = remote_host.migrate(vm, mig_timeout, mig_protocol,
                                      during_migrate)
        ping_pong = params.get("ping_pong", 0)
        for i in xrange(int(ping_pong)):
            if type(dest_vm) == type(vm):
                logging.info("ping...")
                dest_vm = remote_host.migrate(dest_vm, mig_timeout,
                                              mig_protocol, during_migrate)
            else:
                logging.info("pong...")
                dest_vm = virt_test_utils.migrate(dest_vm, env, mig_timeout,
                                                 mig_protocol, mig_cancel)

        if guest_stress_test:
            guest_stress_stop()

        # run some functions after migrate finish.
        post_migrate = get_functions(params.get("post_migrate"), locals())
        for func in post_migrate:
            func()

        # Log into the guest again
        logging.info("Logging into guest after migration...")
        session2 = vm.wait_for_login(timeout=login_timeout)
        if not session2:
            raise error.TestFail("Could not log into guest after migration")
        logging.info("Logged in after migration")

        # Make sure the background process is still running
        session2.cmd(check_command, timeout=30)

        # Get the output of migration_test_command
        output = session2.cmd_output(test_command)

        # Compare output to reference output
        if reference_output and (output != reference_output):
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

        kvm_cross_host_utils.test_finish(remote_host, xmlrpc_server,
                                         login_timeout)

    if session2:
        session2.close()
    if session:
        session.close()
