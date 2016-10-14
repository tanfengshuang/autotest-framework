import re, string, logging, random
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import kvm_monitor
from autotest_lib.client.virt import virt_env_process
from autotest_lib.client.virt import virt_utils


def run_physical_resources_check(test, params, env):
    """
    Check physical resources assigned to KVM virtual machines:
    1) Log into the guest
    2) Verify whether cpu counts ,memory size, nics' model,
       count and drives' format & count, drive_serial, UUID
       reported by the guest OS matches what has been assigned
       to the VM (qemu command line)
    3) Verify all MAC addresses for guest NICs

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    if params.get("catch_serial_cmd") is not None:
        length = int(params.get("length", "20"))
        id_leng = random.randint(0, length)
        drive_serial = ""
        convert_str = "!\"#$%&\'()*+./:;<=>?@[\\]^`{|}~"
        drive_serial = virt_utils.generate_random_string(id_leng,
                                      ignore_str=",", convert_str=convert_str)

        params["drive_serial"] = drive_serial

        vm = "vm1"
        vm_params = params.object_params(vm)
        virt_env_process.preprocess_vm(test, vm_params, env, vm)
        vm = env.get_vm(vm)
    else:
        vm = env.get_vm(params["main_vm"])

    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    chk_timeout=int(params.get("chk_timeout"))
    session = vm.wait_for_login(timeout=timeout)

    vcpu_sockets = params.get("vcpu_sockets")
    vcpu_cores = params.get("vcpu_cores")
    vcpu_threads = params.get("vcpu_threads")
    sockets_chk_cmd = params.get("sockets_chk_cmd")
    cores_chk_cmd = params.get("cores_chk_cmd")
    threads_chk_cmd = params.get("threads_chk_cmd")
    chk_str = params.get("mem_chk_re_str")

    logging.info("Starting physical resources check test")
    logging.info("Values assigned to VM are the values we expect "
                 "to see reported by the Operating System")
    # Define a failure counter, as we want to check all physical
    # resources to know which checks passed and which ones failed
    n_fail = 0

    # Check cpu count
    logging.info("CPU count check")
    expected_cpu_nr = int(params.get("smp"))
    actual_cpu_nr = vm.get_cpu_count()
    if expected_cpu_nr != actual_cpu_nr:
        n_fail += 1
        logging.error("CPU count mismatch:")
        logging.error("    Assigned to VM: %s", expected_cpu_nr)
        logging.error("    Reported by OS: %s", actual_cpu_nr)

    # Check sockets num
    logging.info("Sockets num check")
    if vcpu_sockets:
        expected_sockets_n = int(vcpu_sockets)
    else:
        expected_sockets_n = expected_cpu_nr/int(vcpu_cores)/int(vcpu_threads)
    s, sockets_n = session.get_command_status_output(sockets_chk_cmd,
                           timeout=chk_timeout)
    if s != 0:
        raise error.TestError("Failed to get guest sockets num %s" % sockets_n)
    actual_sockets_n = int(re.findall(chk_str, sockets_n)[0])
    if expected_sockets_n != actual_sockets_n:
        n_fail += 1
        logging.error("Sockets num mismatch:")
        logging.error("    Assigned to VM: %s" % expected_sockets_n)
        logging.error("    Reported by OS: %s" % actual_sockets_n)
    else:
        logging.info("Sockets check pass. Expected: %s, Actual: %s" %
                    (expected_sockets_n, actual_sockets_n))

    # Check cores num
    logging.info("Cores num check")
    if vcpu_cores:
        expected_cores_n = int(vcpu_cores)
    else:
        expected_cores_n = expected_cpu_nr/int(vcpu_sockets)/int(vcpu_threads)
    s, cores_n = session.get_command_status_output(cores_chk_cmd,
                         timeout=chk_timeout)
    if s != 0:
        raise error.TestError("Failed to get guest cores num")
    actual_cores_n = int(re.findall(chk_str, cores_n)[0])
    if expected_cores_n != actual_cores_n:
        n_fail += 1
        logging.error("Cores num mismatch:")
        logging.error("    Assigned to VM: %s" % expected_cores_n)
        logging.error("    Reported by OS: %s" % actual_cores_n)
    else:
        logging.info("Cores check pass. Expected: %s, Aucual: %s" %
                    (expected_cores_n, actual_cores_n))

    # Check threads num
    logging.info("Threads num check")
    if vcpu_threads:
        expected_threads_n = int(vcpu_threads)
    else:
        expected_threads_n = expected_cpu_nr/int(vcpu_cores)/int(vcpu_sockets)

    if params.get("threads_chk_cmd"):
        s, threads_n = session.get_command_status_output(threads_chk_cmd,
                                  timeout=chk_timeout)
        if s != 0:
            raise error.TestError("Failed to get guest threads num")
        actual_threads_n = int(re.findall(chk_str, threads_n)[1])
    else:
        s, siblings_n = session.get_command_status_output(
                        params.get("get_siblings_num"))
        if s != 0:
            raise error.TestError("Failed to get guest sibling num")
        actual_threads_n = int(siblings_n.split()[-1])/actual_cores_n

    if expected_threads_n != actual_threads_n:
        n_fail += 1
        logging.error("Threads num mismatch:")
        logging.error("    Assigned to VM: %s" % expected_threads_n)
        logging.error("    Reported by OS: %s" % actual_threads_n)
    else:
        logging.info("Threads check pass. Expected: %s Actual: %s" %
                    (expected_threads_n, actual_threads_n))

    # Check the cpu vendor_id
    expected_vendor_id = params.get("cpu_vendor_id")
    cpu_vendor_id_chk_cmd = params.get("cpu_vendor_id_chk_cmd")
    # seems that vendor_id does not work on rhel5.x
    if expected_vendor_id and cpu_vendor_id_chk_cmd and \
            vm.host_version >= "rhel6.0":
        logging.info("Expected cpu vendor_id: %s" % expected_vendor_id)
        vid_output = session.cmd_output(cpu_vendor_id_chk_cmd)

        logging.debug("Guest cpu vendor_id:\n%s" % vid_output)
        if expected_vendor_id in vid_output:
            logging.info("CPU vendor id check passed.")
        else:
            n_fail += 1
            logging.error("CPU vendor id check failed.")

    # Check memory size
    logging.info("Memory size check")
    expected_mem = int(params.get("mem"))
    actual_mem = vm.get_memory_size()
    if actual_mem != expected_mem:
        n_fail += 1
        logging.error("Memory size mismatch:")
        logging.error("    Assigned to VM: %s", expected_mem)
        logging.error("    Reported by OS: %s", actual_mem)

    # Define a function for checking number of hard drivers & NICs
    def check_num(devices, info_cmd, check_str):
        f_fail = 0
        expected_num = params.objects(devices).__len__()
        o = ""
        try:
            o = vm.monitor.info(info_cmd)
        except kvm_monitor.MonitorError, e:
            f_fail += 1
            logging.error(e)
            logging.error("info/query monitor command failed (%s)", info_cmd)

        actual_num = string.count(o, check_str)
        if expected_num != actual_num:
            f_fail += 1
            logging.error("%s number mismatch:")
            logging.error("    Assigned to VM: %d", expected_num)
            logging.error("    Reported by OS: %d", actual_num)
        return expected_num, f_fail

    logging.info("Hard drive count check")
    n_fail += check_num("images", "block", "type=hd")[1]

    logging.info("NIC count check")
    n_fail += check_num("nics", "network", "model=")[1]

    # Define a function for checking hard drives & NICs' model
    def chk_fmt_model(device, fmt_model, info_cmd, regexp):
        f_fail = 0
        devices = params.objects(device)
        for chk_device in devices:
            expected = params.object_params(chk_device).get(fmt_model)
            if not expected:
                expected = "rtl8139"
            o = ""
            try:
                o = vm.monitor.info(info_cmd)
            except kvm_monitor.MonitorError, e:
                f_fail += 1
                logging.error(e)
                logging.error("info/query monitor command failed (%s)",
                              info_cmd)

            device_found = re.findall(regexp, o)
            logging.debug("Found devices: %s", device_found)
            found = False
            for fm in device_found:
                if expected in fm:
                    found = True

            if not found:
                f_fail += 1
                logging.error("%s model mismatch:")
                logging.error("    Assigned to VM: %s", expected)
                logging.error("    Reported by OS: %s", device_found)
        return f_fail

    logging.info("NICs model check")
    f_fail = chk_fmt_model("nics", "nic_model", "network", "model=(.*),")
    n_fail += f_fail

    logging.info("Drive format check")
    f_fail = chk_fmt_model("images", "drive_format", "block", "(.*)\: type=hd")
    n_fail += f_fail

    logging.info("Network card MAC check")
    o = ""
    try:
        o = vm.monitor.info("network")
    except kvm_monitor.MonitorError, e:
        n_fail += 1
        logging.error(e)
        logging.error("info/query monitor command failed (network)")
    found_mac_addresses = re.findall("macaddr=(\S+)", o)
    logging.debug("Found MAC adresses: %s", found_mac_addresses)

    num_nics = len(params.objects("nics"))
    for nic_index in range(num_nics):
        mac = vm.get_mac_address(nic_index)
        if not string.lower(mac) in found_mac_addresses:
            n_fail += 1
            logging.error("MAC address mismatch:")
            logging.error("    Assigned to VM (not found): %s", mac)

    # Define a function to verify UUID & Serial number
    def verify_device(expect, name, verify_cmd, strict=False):
        f_fail = 0
        if verify_cmd:
            actual = session.cmd_output(verify_cmd)
            if not strict:
                if not string.upper(expect) in actual:
                    f_fail += 1
            else:
                if expect.strip() != actual.strip():
                    f_fail += 1

            if f_fail > 0:
                logging.error("%s mismatch:" % name)
                logging.error("    Assigned to VM: %s" % expect)
                logging.error("    Reported by OS: %s" % actual)
        return f_fail

    logging.info("UUID check")
    if vm.get_uuid():
        f_fail = verify_device(vm.get_uuid(), "UUID",
                               params.get("catch_uuid_cmd"))
        n_fail += f_fail

    logging.info("Hard Disk serial number check")
    catch_serial_cmd = params.get("catch_serial_cmd")
    serial_number = "".join(re.split(r"\\", params.get("drive_serial")))
    f_fail = verify_device(serial_number, "Serial",
                           catch_serial_cmd, strict=True)
    n_fail += f_fail


    def check_vio_driver():
        """
        only check if the MS Windows VirtIO driver is digital signed.
        """
        f_fail = 0
        chk_cmd = params.get("vio_driver_chk_cmd")
        if chk_cmd:
            logging.info("Virtio Driver Check")
            chk_output = session.cmd_output(chk_cmd, timeout=chk_timeout)
            logging.debug("VirtIO driver check output:\n%s" % chk_output)
            if "FALSE" in chk_output:
                f_fail += 1
                logging.error("VirtIO driver is not digital signed!")
        return f_fail

    n_fail += check_vio_driver()

    if n_fail != 0:
        raise error.TestFail("Physical resources check test reported %s "
                             "failures. Please verify the test logs." % n_fail)

    session.close()
