import logging
from autotest_lib.client.common_lib import error


def run_lvm(test, params, env):
    """
    KVM reboot test:
    1) Log into a guest
    2) Create a volume group and add both disks as pv to the Group
    3) Create a logical volume on the VG
    5) `fsck' to check the partition that LV locates

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    login_timeout = int(params.get("login_timeout", 360))
    session = vm.wait_for_login(timeout=login_timeout)

    vg_name = "volgrp_kvm_test"
    lv_name = "lv_kvm_test"
    lv_path = "/dev/%s/%s" % (vg_name, lv_name)
    disks = params.get("disks", "/dev/hdb /dev/hdc")
    clean = params.get("clean", "yes")
    timeout = params.get("lvm_timeout", "600")

    try:
        s, o = session.get_command_status_output("pvcreate %s" % disks)
        if s != 0:
            raise error.TestError("Create physical volume failed: %s" % o)
        logging.info("Physical volumes created")

        s, o = session.get_command_status_output("vgcreate %s %s" %
                                                 (vg_name, disks))
        if s != 0:
            raise error.TestError("Create volume group failed: %s" % o)
        logging.info("Volume group %s created" % vg_name)

        # Activate the volume group
        s, o = session.get_command_status_output("vgchange -ay %s" % vg_name)
        if s != 0:
            raise error.TestError("Activate volume group failed: %s" % o)

        # Create a logical volume on this VG
        s, o = session.get_command_status_output("lvcreate -L2000 -n %s %s" %
                                                 (lv_name, vg_name))
        if s != 0:
            raise error.TestError("Create volume failed: %s" % o)

        # Create file system on the logical volume
        s, o = session.get_command_status_output("yes|mkfs.ext3 %s" % lv_path,
                                                 timeout = int(timeout))
        if s != 0:
            raise error.TestError("Failed to create file system on lv: %s" % o)

        s, o = session.get_command_status_output("mount %s /mnt" % lv_path)
        if s != 0:
            raise error.TestError("Failed to mount the logical volume: %s" % o)

        s, o = session.get_command_status_output("umount %s" % lv_path)
        if s != 0 :
            logging.error(o)
            raise error.TestError("Failed to umount the lv %s" % lv_path)

        s, o = session.get_command_status_output("fsck %s" % lv_path,
                                                 timeout = int(timeout))
        if s != 0:
            logging.error(o)
            raise error.TestFail("Error occurred while fsck: %s" % o)

        # need remount it for the following test
        if clean == "no":
            s, o = session.get_command_status_output("mount %s /mnt" % lv_path)
            if s != 0:
                raise error.TestError("Fail to mount the logical volume: %s" % o)
            logging.info(session.get_command_output("mount"))

    finally:
        if clean == "yes":
            cmd = "umount /mnt;lvremove %s;vgchange -a n %s;vgremove -f %s"
            session.get_command_status(cmd % (lv_name, vg_name, vg_name))
