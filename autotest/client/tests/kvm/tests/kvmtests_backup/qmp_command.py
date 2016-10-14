import logging, time, os, commands, re
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_utils, kvm_monitor


def run_qmp_command(test, params, env):
    """
    Test qmp event notification, this case will:
    1) Start VM with qmp enable.
    2) Connect to qmp port then run qmp_capabilities command.
    3) make testing event in guest os.
    4) Verify that qmp through corresponding event notification.

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environmen.
    """

    if not virt_utils.has_option("qmp"):
        logging.info("Host qemu does not support qmp. Ignore this case!")
        return
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()

    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    callback = {"host_cmd": commands.getoutput,
                "guest_cmd": session.get_command_output,
                "monitor_cmd": vm.monitor.send_args_cmd,
                "qmp_cmd": vm.monitors[1].send_args_cmd}

    def send_cmd(cmd):
        if cmd_type in callback.keys():
            return callback[cmd_type](cmd)
        else:
            raise error.TestError("cmd_type is not supported")
            return ("")

    def check_result(qmp_o, o=None):
        """
        Check test result with difference way accoriding to
        result_check.
        result_check = equal, will compare cmd_return_value with qmp
        command output.
        result_check = contain, will try to find cmd_return_value in qmp
        command output.
        result_check = m_equal_q, will compare key value in monitor command
        output and qmp command output.
        result_check = m_in_q, will try to find monitor command output's key
        value in qmp command output.

        @param qmp_o: output from pre_cmd, qmp_cmd or post_cmd.
        @param qmp_o: output from pre_cmd, qmp_cmd or post_cmd or an execpt
        result set in config file.
        """
        logging.debug("result_check : %s" % result_check)
        if result_check == "equal":
            value = o
            if value != str(qmp_o):
                raise error.TestFail("QMP command return value is not match"
                                     " with expect result. Expect result is:%s"
                                     "\n Actually result is:%s\n"
                                     % (value, qmp_o))
        elif result_check == "contain":
            values = o.split(';')
            for value in values:
                if value not in str(qmp_o):
                    raise error.TestFail("QMP command output does not contain"
                                         " expect result. Expect result is:%s"
                                         "\n Actually result is:%s\n"
                                          % (value, qmp_o))
        elif result_check == "not_contain":
            values = o.split(';')
            for value in values:
                if value in str(qmp_o):
                    raise error.TestFail("QMP command output contains unexpect"
                                         " result. Unxpect result is:%s"
                                         "\n Actually result is:%s\n"
                                          % (value, qmp_o))
        elif result_check == "m_equal_q":
            res = o.splitlines(True)
            if type(qmp_o) != type(res):
                len_o = 1
            else:
                len_o = len(qmp_o)
            if len(res) != len_o:
                return False
            re_str = "(\w+)=(\w+)"
            if len_o > 1:
                for i in range(len(res)):
                    matches = re.findall(re_str, res[i])
                    for key, value in matches:
                        if '0x' in value:
                            value = long(value, 16)
                            if value != qmp_o[i][key]:
                                return False
                        elif qmp_cmd == "query-block":
                            cmp_str = "u'%s': u'%s'" % (key, value)
                            if '0' == value:
                                cmp_str_b = "u'%s': False" % key
                            elif '1' == value:
                                cmp_str_b = "u'%s': True" % key
                            else:
                                cmp_str_b = cmp_str
                            if cmp_str not in str(qmp_o[i]) and\
                               cmp_str_b not in str(qmp_o[i]):
                                return False
                        else:
                            if value not in str(qmp_o[i][key]) and\
                               str(bool(int(value))) not in str(qmp_o[i][key]):
                                return False
            else:
                matches = re.findall(re_str, res[0])
                for key, value in matches:
                    if '0x' in value:
                        value = long(value, 16)
                        if value != qmp_o[0][key]:
                            return False
                    elif qmp_cmd == "query-balloon":
                        if int(value)*1024*1024 != qmp_o[key] and\
                        value not in str(qmp_o[key]):
                            return False
                    else:
                        if value not in str(qmp_o[key]):
                            return False
            return True
        elif result_check == "m_in_q":
            res = o.splitlines(True)
            for i in  range(len(res)):
                params = res[0].rstrip().split()
                for param in params:
                    # use "".join to ignore space in qmp_o
                    try:
                        str_o = "".join(str(qmp_o.values()))
                    except AttributeError:
                        str_o = qmp_o
                    if param.rstrip() not in str(str_o):
                        return False
                return True

    pre_cmd = params.get("pre_cmd")
    qmp_cmd = params.get("qmp_cmd")
    qmp_protocol = params.get("qmp")
    cmd_type = params.get("event_cmd_type")
    post_cmd = params.get("post_cmd")
    result_check = params.get("cmd_result_check")
    cmd_return_value = params.get("cmd_return_value")

    timeout = int(params.get("check_timeout",360))
    if pre_cmd is not None:
        pre_o = send_cmd(pre_cmd)
        logging.debug("Pre-command is:%s\n Output is: %s\n" % (pre_cmd, pre_o))
    try:
        #vm.monitors[1] is first qmp monitor. vm.monitors[0] is human monitor
        o = vm.monitors[1].send_args_cmd(qmp_cmd)
        logging.debug("QMP command is:%s \n Output is:%s\n" % (qmp_cmd,o))
    except kvm_monitor.QMPCmdError, e:
        if params.get("negative_test") == 'yes':
            logging.debug("Negative QMP command: %s\n output:%s\n"
                           % (qmp_cmd, e))
            if params.get("negative_check_point"):
                check_point = params.get("negative_check_point")
                if check_point not in str(e):
                    raise error.TestFail("%s not in exception %s"
                                                       % (check_point, e))
        else:
            raise error.TestFail(e)
    except kvm_monitor.MonitorProtocolError, e:
        logging.error("Monitor protocol error.")
        raise error.TestFail(e)
    except Exception, e:
        logging.error("QMP command fail.")
        raise error.TestFail(e)

    if post_cmd is not None:
        post_o = send_cmd(post_cmd)
        logging.debug("Post-command:%s\n Output is:%s\n" % (post_cmd, post_o))

    if result_check is not None:
        if result_check == "equal" or result_check == "contain":
            check_result(o, cmd_return_value)
        elif 'post' in result_check:
            result_check = '_'.join(result_check.split('_')[1:])
            check_result(post_o, cmd_return_value)
        else:
            if check_result(o, post_o):
                logging.info("QMP command successfully")
            else:
                raise error.TestFail("QMP command fail, please refer to log "
                                     "for details")
    session.close()
