import logging, time, random, os, commands, re
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import aexpect
from autotest_lib.client.virt import virt_test_utils


def run_ksm_base(test, params, env):
    """
    Test how KSM (Kernel Shared Memory) act when more than physical memory is
    used. In second part we also test how KVM handles a situation when the host
    runs out of memory (it is expected to pause the guest system, wait until
    some process returns memory and bring the guest back to life)

    @param test: kvm test object.
    @param params: Dictionary with test parameters.
    @param env: Dictionary with the test wnvironment.
    """
    def _start_allocator(vm, session, timeout):
        """
        Execute allocator.py on a guest, wait until it is initialized.

        @param vm: VM object.
        @param session: Remote session to a VM object.
        @param timeout: Timeout that will be used to verify if allocator.py
                started properly.
        """
        logging.debug("Starting allocator.py on guest %s", vm.name)
        session.sendline("python /tmp/ksm_overcommit_guest.py")
        try:
            (match, data) = session.read_until_last_line_matches(
                                                            ["PASS:", "FAIL:"],
                                                            timeout)
        except aexpect.ExpectProcessTerminatedError, e:
            raise error.TestFail("Command allocator.py on vm '%s' failed: %s" %
                                 (vm.name, str(e)))

    def _execute_allocator(command, vm, session, timeout):
        """
        Execute a given command on allocator.py main loop, indicating the vm
        the command was executed on.

        @param command: Command that will be executed.
        @param vm: VM object.
        @param session: Remote session to VM object.
        @param timeout: Timeout used to verify expected output.

        @return: Tuple (match index, data)
        """
        logging.debug("Executing '%s' on allocator.py loop, vm: %s, timeout: %s",
                      command, vm.name, timeout)
        session.sendline(command)
        try:
            (match, data) = session.read_until_last_line_matches(
                                                             ["PASS:","FAIL:"],
                                                             timeout)
        except aexpect.ExpectProcessTerminatedError, e:
            e_str = ("Failed to execute command '%s' on allocator.py, "
                     "vm '%s': %s" % (command, vm.name, str(e)))
            raise error.TestFail(e_str)
        return (match, data)

    timeout = float(params.get("login_timeout", 240))
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login(timeout=timeout)
    
    try: 
        logging.info("Start to prepare env in host")
        # Check ksm module status
        ksm_module = params.get("ksm_module")
        if  ksm_module:
            module_status, o = commands.getstatusoutput("lsmod |grep %s" % \
                                                        ksm_module)
            if module_status == 256:
                s, o = commands.getstatusoutput("modprobe %s" % ksm_module)
                if s != 0:
                    raise error.TestError("Can not insert ksm module in host") 
            
        # Prepare env for KSM
        s, ksmtuned_id = commands.getstatusoutput("ps -C ksmtuned -o pid=")
        if ksmtuned_id:
            logging.info("Turn off ksmtuned in host")
            s, o = commands.getstatusoutput("kill -9 %s" % ksmtuned_id)
        status_query_cmd = params.get("status_query_cmd")
        setup_cmd = params.get("setup_cmd")
        s, status = commands.getstatusoutput(status_query_cmd)
        if int(re.findall("\d+", status)[0]) == 0:
            s, o = commands.getstatusoutput(setup_cmd)
            if s != 0:
                raise error.TestError("Can not setup KSM: %s" % o)
        
        #prepare work in guest 
        logging.info("Turn off swap in guest")
        s, o = session.cmd_status_output("swapoff -a")
        vm.copy_files_to("%s/scripts/ksm_overcommit_guest.py" % test.bindir, "/tmp")
        test_type = params.get("test_type")
        shared_mem = params.get("shared_mem")
        fill_timeout = int(shared_mem) / 10 
        query_cmd = params.get("query_cmd")
        query_regex = params.get("query_regex")
        random_bits = params.get("random_bits")
        seed = random.randint(0, 255)

        s, sharing_page_0 = commands.getstatusoutput(query_cmd)
        if query_regex:
            sharing_page_0 = re.findall(query_regex, sharing_page_0)[0]

        _start_allocator(vm, session, 60)
        mem_fill = "mem = MemFill(%s, 0, %s)" % (shared_mem, seed)
        _execute_allocator(mem_fill, vm, session, fill_timeout)
        cmd = "mem.value_fill()"
        _execute_allocator(cmd, vm, session, fill_timeout)
        time.sleep(120)

        s, sharing_page_1 = commands.getstatusoutput(query_cmd)
        if query_regex:
            sharing_page_1 = re.findall(query_regex, sharing_page_1)[0]
 
        split = params.get("split")
        if split == "yes":
            if test_type == "negative":
                cmd = "mem.static_random_fill(%s)" % random_bits
            else:
                cmd = "mem.static_random_fill()"
        _execute_allocator(cmd, vm, session, fill_timeout)
        time.sleep(120)

        s, sharing_page_2 = commands.getstatusoutput(query_cmd)
        if query_regex:
            sharing_page_2 = re.findall(query_regex, sharing_page_2)[0]

        sharing_page = [sharing_page_0, sharing_page_1, sharing_page_2]
        for i in sharing_page:
            if re.findall("[A-Za-z]", i):
                data = i[0:-1]
                unit = i[-1]
                index = sharing_page.index(i)
                if unit == "g":
                    sharing_page[index] = virt_test_utils.aton(data) * 1024
                else:
                    sharing_page[index] = virt_test_utils.aton(data)
 
        fail_type = 0
        if test_type == "disable":
            if int(sharing_page[0]) != 0 and int(sharing_page[1]) != 0:
                fail_type += 1 
        else:
            if int(sharing_page[0]) >= int(sharing_page[1]):
                fail_type += 2
            if int(sharing_page[1]) <= int(sharing_page[2]):
                fail_type += 4
       
        fail = ["Sharing page increased abnormal", 
                "Sharing page didn't increase", "Sharing page didn't split"]
 
        if fail_type != 0:
            turns = 0
            while (fail_type > 0):
                if fail_type % 2 == 1:
                    logging.error(fail[turns])
                fail_type = fail_type / 2
                turns += 1
            raise error.TestFail("KSM test failed: %s %s %s" % (sharing_page_0, sharing_page_1, sharing_page_2))

    finally:
        if ksm_module:
            if module_status == 256:
                logging.info("unload ksm module")
                s, o = commands.getstatusoutput("modprobe -r %s" % ksm_module)
        if ksmtuned_id:
           logging.info("Restart ksmtuned in host")
           os.system("/bin/bash /usr/sbin/ksmtuned")
        if int(re.findall("\d+", status)[0]) == 0:
            logging.info("Reset the ksm env in host")
            if re.findall("ksmctl", setup_cmd):
                cmd = "ksmctl stop"
            else:
                cmd = "echo 0 > %s" % re.split(">", setup_cmd)[-1]
            s, o = commands.getstatusoutput(cmd)
        session.close()
