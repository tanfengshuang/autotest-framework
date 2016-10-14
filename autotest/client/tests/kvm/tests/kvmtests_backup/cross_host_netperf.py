import logging, commands
from autotest_lib.client.common_lib import error
import kvm_cross_host_utils
from autotest_lib.client.tests.kvm.tests import autotest


def run_cross_host_netperf(test, params, env):
    """
    Run netperf2 on two guests:
    1) One as client while the other is server
    2) Run netserver on server guest using control.server
    3) Run netperf on client guest using control.client

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment
    """
    server_type = params.get("server_type")
    client_type = params.get("client_type")

    login_timeout = int(params.get("login_timeout", 360))

    server = None
    client = None

    # init server object.
    if server_type == "host":
        server = kvm_cross_host_utils.RemoteHost("localhost", params)
    elif server_type == "guest":
        server_name = params.get("server_vm")
        if not server_name:
            raise error.TestError("Could get server vm name.")
        server = env.get_vm(params["main_vm"])
        server.verify_alive()
    elif server_type == "remotehost":
        server_address = params.get("dsthost")
        remote_host = kvm_cross_host_utils.RemoteHost(server_address, params)
        server = remote_host
    elif server_type == "remotevm":
        server_address = params.get("dsthost")
        remote_host = kvm_cross_host_utils.RemoteHost(server_address, params)
        remote_vm = params.get("server_vm")
        if not remote_vm:
            raise error.TestError("Could get server vm name.")
        server = kvm_cross_host_utils.RemoteVM(remote_host, remote_vm, login_timeout)

    # init client object.
    if client_type == "host":
        client = kvm_cross_host_utils.RemoteHost("localhost", params)
    elif client_type == "guest":
        client_name = params.get("client_vm")
        if not client_name:
            raise error.TestError("Could get client vm name")
        client = env.get_vm(params["main_vm"])
        client.verify_alive()
    elif client_type == "remotehost":
        client_address = params.get("dsthost")
        remote_host = kvm_cross_host_utils.RemoteHost(client_address, params)
        client = remote_host
    elif client_type == "remotevm":
        client_address = params.get("dsthost")
        remote_host = kvm_cross_host_utils.RemoteHost(client_address, params)
        remote_vm = params.get("client_vm")
        if not remote_vm:
            raise error.TestError("Could get client vm name.")
        client = kvm_cross_host_utils.RemoteVM(remote_host, remote_vm, login_timeout)

    if "remote" in server_type or "remote" in client_type:
        # don't start autotest on remote_host now.
        params["remote_test"] = "no"
        # don't start xmlrpc server.
        params["listen_ip"] = None
        kvm_cross_host_utils.test_init(test, params, env)
        if params.get("slaver_peer") == "yes":
            kvm_cross_host_utils.start_vms(test, params, env)

    session_server = None
    server_address = "localhost"
    if server:
        session_server = vm.wait_for_login(timeout=login_timeout)
        server_address = server.get_address()

    session_client = None
    client_address = "localhost"
    if client:
        session_client = vm.wait_for_login(timeout=login_timeout)
        client_address = client.get_address()

    def fix_control(type, session, control):
        content = """
job.run_test('netperf2',
              server_ip='%s',
              client_ip='%s',
              role='%s',
              tag='%s')
""" % (server_address, client_address, type, type)
        cmd = 'echo "%s" > /tmp/%s' % (content, control)

        commands.getoutput(cmd)
        if session:
            session.get_command_output("service iptables stop")
            session.close()
        else:
            commands.getoutput("service iptables stop")

    fix_control("server", session_server, "control.server")
    fix_control("client", session_client, "control.client")

    # Setup netserver on server machine
    logging.info("Setting up server machine")
    params['test_name'] = 'netperf2'
    params['test_timeout'] = '600'
    autotest.run_autotest_background(test, params, env,
                                           test_name="netperf2",
                        test_control_file="/tmp/control.server",
                        machine=server)

    # Run netperf on client machine
    logging.info("Setting up client machine")
    params['test_control_file'] = '/tmp/control.client'
    autotest.run_autotest(test, params, env, machine=client)
