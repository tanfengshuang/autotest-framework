##@ Summary: Profile Test
##@ Description:
##@ Maintainer: Jason Wang <jasowang@redhat.com>, Chen Cao <kcao@redhat.com>
##@ Updated:
##@ Version:    2

import commands
import getopt
import os
import sys
import time

def usage():
    print "python ProfileTest.py [--kernel=`uname -r` --qemu_kvm=`rpm -q kvm`]"


def get_kernel_version():
    kernel = os.uname()[2]
    print "Installed kernel version: %s" % kernel
    return kernel


def get_rpm_version(pkg="qemu-kvm"):
    (s, o) = commands.getstatusoutput("rpm -q %s" % pkg)
    if s != 0:
        print "Warn: Failed to get the version of %s" % pkg
        return "Invalid-Version"

    print "Installed %s version: %s" % (pkg, o)
    return o


def is_cmd_available(cmd="kvm_stat"):
    print "Testing command: %s..." % cmd,
    if os.system("file `which %s`" % cmd) == 0:
        print " Passed!"
        return True
    else:
        print " Failed!"
        return False


def is_mod_loaded(mod="kvm"):
    print "Checking module: %s..." % mod,
    if os.system("lsmod |grep -w %s " % mod) == 0:
        print " Passed!"
        return True
    else:
        print " Failed!"
        return False


def is_proc_launched(proc="STAFProc"):
    print "Checking process: %s..." % proc,
    if os.system("ps -eo command |grep -w ^%s " % proc) == 0:
        print " Passed!"
        return True
    else:
        print " Failed!"
        return False


def rmdir_silent(dir_name):
    """
    return False when error happens.
    """
    try:
        os.rmdir(dir_name)
    except OSError, err:
        print str(err)
        return False
    return True


def is_nfs_mount_good():
    print "Checking nfs mount..."
    tmp_nfs_dir = "/tmp/%s" % time.time()
    try:
        os.mkdir(tmp_nfs_dir)
    except OSError, err:
        print "nfs: failed to create tmp nfs mount point: %s" % tmp_nfs_dir
        print str(err)
        return False

    nfs_remote = "10.66.90.128:/vol/S2/kvmauto/linux_img"
    # mount
    if os.system("mount %s %s" % (nfs_remote, tmp_nfs_dir)):
        print "nfs: failed to mount nfs %s to %s" % (nfs_remote, tmp_nfs_dir)
        rmdir_silent()
        return False
    # umount
    if os.system("umount %s" % tmp_nfs_dir):
        print "nfs: failed to umount nfs %s from %s" % (nfs_remote, tmp_nfs_dir)
        rmdir_silent()
        return False

    # cleanup and return
    return rmdir_silent(tmp_nfs_dir)


def is_log_prepared():
    print "Checking virtlab log dir...",
    cmd = "mount |grep log |grep RHEV |grep results"
    if os.system(cmd) != 0:
        print " Failed!"
        return False
    print " Passed!"
    return True


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hk:q:",
                                   ["help", "kernel=", "qemu_kvm="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(-1)

    error_nr = 0
    error_list = []
    ## versions
    # kernel, qemu-kvm

    # expected value
    kernel = None
    qemu_kvm = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(-1)
        elif o in ("-k", "--kernel"):
            kernel = a
        elif o in ("-q", "--qemu_kvm"):
            qemu_kvm = a

    print "kernel version: %s" % kernel
    print "qemu-kvm version: %s" % qemu_kvm

    # empty string or None value to skip the check
    if kernel and kernel != get_kernel_version():
        print "Error, kernel version does not match!"
        error_nr += 1
        error_list.append("kernel_version")

    if qemu_kvm and \
            not (qemu_kvm == get_rpm_version("qemu-kvm") \
                 or qemu_kvm == get_rpm_version("kvm")):
        print "Error, qemu-kvm version does not match!"
        error_nr += 1
        error_list.append("kvm_version")


    ## existance
    # sysstat (sar, io_stat and others)
    # qemu-kvm-tools/kvm-tools (for kvm_stat and others)
    cmd_list = ["kvm_stat", "sar"]
    for c in cmd_list:
        if not is_cmd_available(c):
            print "Error, command %s is not available." % c
            error_nr += 1
            error_list.append("cmd_%s" % c)

    ## loaded modules
    # kvm, kvm_intel/kvm_amd
    if not is_mod_loaded("kvm"):
        print "Error: Module 'kvm' is not loaded!"
        error_nr += 1
        error_list.append("kmod_kvm")
    if not (is_mod_loaded("kvm_intel") or is_mod_loaded("kvm_amd")):
        print "Error: Module 'kvm_intel/amd' is not loaded!"
        error_nr += 1
        error_list.append("kmod_kvm_arch")


    # nfs mounting, and log dir is mounted
    if not is_nfs_mount_good():
        print "Error: NFS mounting does not work!"
        error_nr += 1
        error_list.append("nfs_mount")
    if not is_log_prepared():
        print "Error: virtlab log dir is not mounted"
        error_nr += 1
        error_list.append("virtlab_log_dir")

    # STAF is launched?
    proc_list = ['STAFProc']
    for p in proc_list:
        if not is_proc_launched(p):
            print "Error: Process '%s' is not Launched" % p
            error_nr += 1
            error_list.append("proc_%s" % p)

    print "So far so good, lets run some tests..."
    # basic tests
    os.system("python ConfigTest.py")

    if error_nr == 0:
        print "Everything is OK. Great!"
    else:
        print "%d failure(s) found! Pls check the log for details." % error_nr
        print "error list: %s" % str(error_list)


if __name__ == "__main__":
    main()
