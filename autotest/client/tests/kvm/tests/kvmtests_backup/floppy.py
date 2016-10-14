import logging, time
from autotest_lib.client.common_lib import error

def run_floppy(test, params, env):
    """
    Test virtual floppy of guest:

    1)Create a floppy disk image on host
    2)start the guest with this floppy image.
    3)make a file system on guest virtual floppy
    4)calculate md5sum value of a file and copy it into floppy.
    5)verify whether the md5sum is match

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=timeout)

    dest_dir = params.get("mount_dir")
    # If mount_dir specified, treat guest as a Linux OS
    # Some Linux distribution does not load floppy at boot and Windows
    # needs time to load and init floppy driver
    if dest_dir:
        status = session.get_command_status("modprobe floppy")
    else:
        time.sleep(20)

    # Format floppy disk before using it
    format_cmd = params.get("format_floppy_cmd")
    s, o = session.get_command_status_output(format_cmd, timeout=120)
    if s != 0:
        raise error.TestError("Failed to format guest floppy disk: %s" % o)
    logging.info("Floppy disk formatted successfully")

    source_file = params.get("source_file")
    dest_file = params.get("dest_file")

    if dest_dir:
        s, o = session.get_command_status_output("mount /dev/fd0 %s" % dest_dir)
        if s != 0:
            raise error.TestError("Failed to mount floppy, reason: %s" % o)

    s, o = session.get_command_status_output(params.get("test_floppy_cmd"))
    if s != 0:
        raise error.TestFail("Test floppy command failed: %s" % o)

    try:
        copy_cmd = "%s %s %s" % (params.get("copy_cmd"), source_file, dest_file)
        s, o = session.get_command_status_output(copy_cmd)
        if s != 0:
            raise error.TestError("Failed to copy file; Reason: %s" % o)
        logging.info("Succeed to copy file '%s' into floppy disk" % source_file)

        # Check whether the file is unchanged after copy
        logging.info("Comparing both files to see whether it is unchanged")
        check_cmd = "%s %s %s" % (params.get("diff_file_cmd"),
                                  source_file, dest_file)
        if session.get_command_status(check_cmd) != 0:
            raise error.TestFail("Both files differs between before and after"
                                 "copy")
    finally:
        clean_cmd = "%s %s" % (params.get("clean_cmd"), dest_file)
        session.get_command_status(clean_cmd)
        if dest_dir:
            session.get_command_status("umount %s" % dest_dir)
        session.close()
