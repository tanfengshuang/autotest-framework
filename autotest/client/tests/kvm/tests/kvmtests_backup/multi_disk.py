import logging, re, random
from autotest_lib.client.common_lib import error

def run_multi_disk(test, params, env):
    """
    Test multi disk suport of guest, this case will:
    1)create disks image in configuration file
    2)start the guest with those disks.
    3)format those disks.
    4)cope file into / out of those disks.
    5)compare the original file and the copyed file by md5 or fc comand.

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    images = params.get("images").split()
    image_num = len(images)
    disk_num = 0
    file_system = params.get("file_system").split()
    fs_num = len(file_system)
    cmd_timeout = float(params.get("cmd_timeout", 360))
    re_str = params.get("re_str")
    block_list = params.get("block_list").split()
    try:
        if params.get("clean_cmd"):
            cmd = params.get("clean_cmd")
            session.get_command_status_output(cmd)
        if params.get("pre_cmd"):
            cmd = params.get("pre_cmd")
            (s,output) = session.get_command_status_output(cmd,
                                                           timeout=cmd_timeout)
            if s != 0:
                raise error.TestFail("Create partition on disk failed.\n"
                                     "Output is:%s \n" % output)
        cmd = params.get("list_volume_command")
        (s,output) = session.get_command_status_output(cmd,
                                                       timeout=cmd_timeout)
        if s != 0:
            raise error.TestFail("List volume command failed.\n"
                                 "Output is:%s\n" % output)
        disks = re.findall(re_str, output)
        disks.sort()
        logging.debug("Volume list that meet regular expressions: %s" % disks)
        if len(disks) < image_num:
            raise error.TestFail("Fail to list all the volume!")

        for disk in disks:
            disk = disk.strip()
            if disk in block_list:
                logging.info("No need check volume %s" % disk)
                continue

            logging.info("Preparing disk: %s..." % disk)
            index = random.randint(0,fs_num -1)

            # Random select one file system from file_system
            fs = file_system[index].strip()
            cmd = params.get("format_command") % (fs, disk)
            (s, output) = session.get_command_status_output(cmd,
                                                            timeout=cmd_timeout)
            if s != 0:
                raise error.TestFail("Format disk failed with output: %s" %
                                                                    output)
            if params.get("mount_command"):
                cmd = params.get("mount_command") % (disk, disk, disk)
                (s, output) = session.get_command_status_output(cmd)
                if s != 0:
                    raise error.TestFail("Mount disk fail with output: %s" %
                                                                     output)

        for disk in disks:
            disk = disk.strip()
            if disk in block_list:
                logging.info("No need check volume %s" % disk)
                continue

            logging.info("Performing I/O on disk: %s..." % disk)
            cmd_list = params.get("cmd_list").split()
            for cmd_l in cmd_list:
                if params.get(cmd_l):
                    cmd = params.get(cmd_l) % disk
                    (s, output) = session.get_command_status_output(cmd,
                                                           timeout=cmd_timeout)
                    if s != 0:
                        raise error.TestFail("command %s fail with output:%s" %
                                                                  (cmd,output))
            cmd = params.get("compare_command")
            (s, output) = session.get_command_status_output(cmd)
            if s != 0:
                raise error.TestFail("Fail to compare two files. Output:%s" %
                                                                      output)
            key_word = params.get("check_result_key_word")
            if key_word and key_word in output:
                logging.debug("Guest's virtual disk %s works fine" % disk)
            elif key_word:
                raise error.TestFail("Two files are not the same!")
            else:
                raise error.TestFail("check_result_key_word is not specified!")
    finally:
        if params.get("umount_command"):
            cmd = params.get("show_mount_cmd")
            (s,output) = session.get_command_status_output(cmd)
            disks = re.findall(re_str, output)
            disks.sort()
            for disk in disks:
                disk = disk.strip()
                if disk in block_list:
                    logging.info("No need umount volume %s" % disk)
                    continue

                cmd = params.get("umount_command") % (disk, disk)
                (s,output) = session.get_command_status_output(cmd)
                if s != 0:
                    raise error.TestFail("Fail to unmount disk. Output is:%s" %
                                                                        output)
        if params.get("post_cmd"):
            cmd = params.get("post_cmd")
            session.get_command_status_output(cmd)
        session.close()

