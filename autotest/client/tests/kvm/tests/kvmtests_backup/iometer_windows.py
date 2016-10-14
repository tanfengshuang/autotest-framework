import logging, time
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import virt_vm


def run_iometer_windows(test, params, env):
    """
    Run Iometer for windows on a windows guest:
    1) Boot guest with second disk
    2) Log into a guest
    3) Install Iometer 
    4) Execute the Iometer test contained in the winutils.iso

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)
    cmd_timeout = int(params.get("cmd_timeout",1200))

    # Create a partition on disk
    time.sleep(120)
    create_partition_cmd = params.get("create_partition_cmd") 
    (s, o) = session.get_command_status_output(cmd=create_partition_cmd,
                                                timeout=cmd_timeout)
    if s != 0:
        raise error.TestFail("Failed to create partition with error: %s" % o)
    logging.info("Output of command of create partition on disk: %s" % o)

    # Format the disk
    format_cmd = params.get("format_cmd")
    (s, o) = session.get_command_status_output(cmd=format_cmd,
                                                timeout=cmd_timeout)
    if s != 0:
        raise error.TestFail("Failed to format with error: %s" % o)
    logging.info("Output of format disk command: %s" % o)

    # Install Iometer
    install_iometer_cmd = params.get("iometer_installation_cmd")
    (s, o) = session.get_command_status_output(cmd=install_iometer_cmd,
                                                timeout=cmd_timeout)
    if s !=0:
        raise error.TestFail("Failed to install iometer with error: %s" % o)
    else:
        logging.info("Complete installation of iometer")

    # Run Iometer
    cmd_reg = params.get("iometer_reg")
    cmd_run = params.get("iometer_run")
    t = int(params.get("iometer_timeout"))
    logging.info("Register Iometer on guest, timeout %ss", cmd_timeout)
    (s, o) = session.cmd_status_output(cmd=cmd_reg, timeout=cmd_timeout)
    if s !=0:
        raise error.TestFail("Failed to register iometer with error: %s" % o)
    else:
        logging.info("Complete iometer register")
    logging.info("Running Iometer command on guest, timeout %ss", cmd_timeout)
    (s, o) = session.cmd_status_output(cmd=cmd_run, timeout=t)
    if s !=0:
        raise error.TestFail("Failed to run iometer with error: %s" % o)
    else:
        logging.info("Completed iometer testing")
    guest_path = params.get("guest_path")
    blk = params.get("drive_format")
    flag = params.get("extra_flags")
    host_path = params.get("host_path") % (blk, flag)
    vm.copy_files_from(guest_path,host_path)

    session.close()
