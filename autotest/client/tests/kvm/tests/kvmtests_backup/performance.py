import logging, time, os, re, commands
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils


def run_performance(test, params, env):
    """
    KVM performance test:

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    test_timeout = float(params.get("test_timeout", 240))
    monitor_cmd = params.get("monitor_command")
    test_cmd = params.get("test_command")
    guest_path = params.get("result_path")
    test_src = params.get("test_src")
    test_patch = params.get("test_patch")
    # Prepare performanc test in guest
    session = vm.wait_for_login(0, 300, 0, 2)
    guest_launcher = os.path.join(test.bindir, "scripts/guest_test_runner.py")
    vm.copy_files_to(guest_launcher, "/tmp")
    MD5 = params.get("MD5")

    tarball = utils.unmap_url_cache(test.tmpdir, test_src, MD5)
    test_src = re.split("/", test_src)[-1]
    vm.copy_files_to(tarball, "/tmp")

    cmd = "rm -rf /tmp/src*; mkdir -p /tmp/src_tmp"
    s, o = session.cmd_status_output(cmd)

    cmd = "tar -xf /tmp/%s -C %s" % (test_src, "/tmp/src_tmp")
    s, o = session.cmd_status_output(cmd)
    if s != 0:
        raise error.TestError("Failed to extract tarball in guest: %s" % o)
    # find the newest file in src tmp directory
    cmd =  "ls -rt /tmp/src_tmp"
    s, o = session.cmd_status_output(cmd)
    if len(o) > 0:
        new_file = re.findall("(.*)\n", o)[-1]
    else:
       raise error.TestError("Can not decompress test file in guest")
    cmd = "mv /tmp/src_tmp/%s /tmp/src" % new_file
    s, o = session.cmd_status_output(cmd)

    if test_patch:
        test_patch_path = os.path.join(test.bindir, "tests_rsc", test_patch)
        vm.copy_files_to(test_patch_path, "/tmp/src")
        cmd = "cd /tmp/src; patch -p1 < /tmp/src/%s" % test_patch
        s, o = session.cmd_status_output(cmd)
        if s != 0:
            raise error.TestError("Can not add modify to tests: %s" % o)

    compile_cmd = params.get("compile_cmd")
    if compile_cmd:
        cmd = "cd /tmp/src; %s" % compile_cmd
        s, o = session.cmd_status_output(cmd)
        if s != 0:
            raise error.TestError("Can not compile test in guest")

    prepare_cmd = params.get("prepare_cmd")
    if prepare_cmd:
        s, o = session.cmd_status_output(prepare_cmd, test_timeout)
        if s != 0:
            raise error.TestError("Can not prepare env for test in guest")
    cmd = "cd /tmp/src; python /tmp/guest_test_runner.py \"%s &> " % monitor_cmd
    cmd += "/tmp/guest_test_result_monitor\"  \"/tmp/src/%s" % test_cmd
    cmd += " &> %s \" \"/tmp/guest_test_result\""
    cmd += " %s" % int(test_timeout)

    test_cmd = cmd
    # Run guest test with monitor
    tag = virt_test_utils.vm_runner_monitor(vm, monitor_cmd, test_cmd,
                                           guest_path, timeout = test_timeout)

    # Result collect
    result_list = ["/tmp/guest_test_result_%s" % tag,
                   "/tmp/monitor_result_%s" % tag,
                   "/tmp/guest_test_monitor_result_%s" % tag]
    guest_results_dir = os.path.join(test.outputdir, "guest_test_results")
    if not os.path.exists(guest_results_dir):
        os.mkdir(guest_results_dir)
    ignore_pattern = params.get("ignore_pattern")
    head_pattern = params.get("head_pattern")
    row_pattern = params.get("row_pattern")
    for i in result_list:
        if re.findall("monitor_result", i):
            result = virt_test_utils.summary_up_result(i, ignore_pattern,
                                head_pattern, row_pattern)
            fd = open("%s.sum" % i, "w")
            sum_info = {}
            head_line = ""
            for keys in result:
                head_line += "\t%s" % keys
                for col in result[keys]:
                    col_sum = "line %s" % col
                    if col_sum in sum_info:
                        sum_info[col_sum] += "\t%s" % result[keys][col]
                    else:
                        sum_info[col_sum] = "%s\t%s" % (col, result[keys][col])
            fd.write("%s\n" % head_line)
            for keys in sum_info:
                fd.write("%s\n" % sum_info[keys])
            fd.close()
            s, o = commands.getstatusoutput("cp %s.sum %s" % (i, guest_results_dir))
        s, o = commands.getstatusoutput("cp %s %s" % (i, guest_results_dir))
    cmd = "rm -rf /tmp/src; rm -rf guest_test*; rm -rf pid_file*"
    s, o = session.cmd_status_output(cmd)
    session.close()
