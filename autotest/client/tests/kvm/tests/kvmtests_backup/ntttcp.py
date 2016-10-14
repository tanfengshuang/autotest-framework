import logging, os
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_utils, virt_test_utils

_receiver_ready = False

def run_ntttcp(test, params, env):
    """
    Run NTttcp on windows guest:

    1) Install NTttcp in server/client side
    2) Start NTttcp in server/client side
    3) Get results

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    login_timeout = int(params.get("login_timeout", 360))
    timeout = int(params.get("timeout"))
    results_path = os.path.join(test.resultsdir,
                                'raw_output_%s' % test.iteration)
    if params.get("platform") == "64":
        platform = "x64"
    else:
        platform = "x86"
    buffers = params.get("buffers").split()
    session_num = params.get("session_num")

    vm_sender = env.get_vm(params["main_vm"])
    vm_sender.verify_alive()
    vm_receiver = None

    receiver_addr = params.get("receiver_address")
    if not receiver_addr:
        vm_receiver = env.get_vm("vm2")
        vm_receiver.verify_alive()
        try:
            sess = None
            sess = vm_receiver.wait_for_login(timeout=login_timeout)
            receiver_addr = vm_receiver.get_address()
            if not receiver_addr:
                raise error.TestError("Could not get receiver %s ip address" % \
                                      vm_sender.name)
        finally:
            if sess:
                sess.close()

    def install_ntttcp(session):
        logging.info("Installing NTttcp...")
        if session.cmd_status(params.get("check_ntttcp_cmd")) == 0:
            logging.info("NTttcp directory already exists")
            return
        ntttcp_install_cmd = params.get("ntttcp_install_cmd")
        ret, output = session.cmd_status_output(ntttcp_install_cmd %
                                                (platform, platform))
        if ret != 0:
            logging.error(output)
            raise error.TestError("Could not install NTTTcp on guest")

    def receiver():
        logging.info("Starting receiver process on %s", receiver_addr)
        if vm_receiver:
            session = vm_receiver.wait_for_login(timeout=login_timeout)
        else:
            username = params.get("username", "")
            password = params.get("password", "")
            prompt = params.get("shell_prompt", "[\#\$]")
            linesep = eval("'%s'" % params.get("shell_linesep", r"\n"))
            client = params.get("shell_client")
            port = int(params.get("shell_port"))
            log_filename = ("session-%s-%s.log" % (receiver_addr,
                            virt_utils.generate_random_string(4)))
            session = virt_utils.remote_login(client, receiver_addr, port,
                                             username, password, prompt,
                                             linesep, log_filename, timeout)
        install_ntttcp(session)
        ntttcp_receiver_cmd = params.get("ntttcp_receiver_cmd")
        global _receiver_ready
        f = open(results_path + ".receiver", 'a')
        for i in xrange(len(buffers)):
            _receiver_ready = True
            r = session.cmd_output(ntttcp_receiver_cmd % (session_num, receiver_addr),
                        timeout=timeout, print_func=logging.debug)
            logging.output("receiver log:%s" % r)
            _receiver_ready = False
            f.write(cmd + '\n')
            f.write(r)
        f.close()
        session.close()

    def _wait():
        global _receiver_ready
        if _receiver_ready:
            return _receiver_ready
        return None

    def sender():
        logging.info("Sarting sender process...")
        session = vm_sender.wait_for_login(timeout=login_timeout)
        install_ntttcp(session)
        ntttcp_sender_cmd = params.get("ntttcp_sender_cmd")
        f = open(results_path + ".sender", 'a')
        try:
            for b in buffers:
                cmd = ntttcp_sender_cmd % (session_num, receiver_addr, b)
                # wait until receiver ready.
                virt_utils.wait_for(_wait, timeout)
                r = session.cmd_output(cmd, timeout=timeout,
                                       print_func=logging.debug)
                f.write(cmd + '\n')
                f.write(r)
        finally:
            f.close()
            session.close()

    bg = virt_test_utils.BackgroundTest(receiver, ())
    bg.start()
    if bg.is_alive():
        sender()
        try:
            bg.join()
        except:
            pass
    else:
        raise error.TestError("Could not start Backgroud receiver thread")
