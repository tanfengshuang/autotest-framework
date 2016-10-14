import os, sys, ConfigParser, commands, re, time
import logging

client_dir = os.path.realpath('kvm-test')
sys.path.insert(0, client_dir)
import setup_modules
setup_modules.setup(base_path=client_dir,root_module_name="autotest_lib.client")
sys.path.pop(0)

from autotest_lib.client.common_lib import utils

sys.path.insert(0, os.path.join(os.getcwd(), 'kvm-test/virt/'))
import common, virt_utils

sys.path.pop(0)

def config_parser(dict):
    section = 'default'
    env_cfg_file = 'env_setup.cfg'

    cf = ConfigParser.ConfigParser()
    cf.read(env_cfg_file)

    for i in cf.options(section):
        dict[i] = cf.get(section, i)

    return dict


def kvm_verify(dict):
    """ Verify whether kvm is loaded in the host """
    if not os.path.exists('/dev/kvm'):
        logging.error("kvm is not loaded in this machine")
        return False

    """ Verify the existence of autotest """
    autotest_client_path = os.path.join(os.getcwd(),'kvm-test')
    if not os.path.exists(autotest_client_path):
        logging.error("autotest is not exist in the path %s" %
                                              autotest_client_path)
        return False

def launch_ksm(dict):
    """ Launch ksm """
    if dict['ksm'] == '1':
        commands.getoutput("modprobe ksm")
        commands.getoutput("ksmctl start 5000 50")
    else:
        commands.getoutput("ksmctl stop")

def link_if_not_exist(src, dst):
    """ prepare symlink
    """
    if not os.path.exists(dst):
        commands.getoutput('ln -s %s %s' % (src,dst))

def link(src, dst):
    """prepare symlink even if it is exist
    """
    commands.getoutput('rm -rf %s' % dst)
    commands.getoutput('ln -s %s %s' % (src,dst))

def mkdir_if_not_exist(dir):
    """ prepare directory or mount point
    """
    if not os.path.exists(dir):
        commands.getoutput('mkdir -p %s' % dir)

def mount_if_not_exist(src, dst, option):
    """ prepare nfs
    """
    result = os.popen("mount").readlines()
    mount = False
    for line in result:
        if src in line and dst in line:
            mount = True
            break
    if mount == True:
        logging.info("%s already mounted to %s" % (src, dst))
    else:
        commands.getoutput("mount %s %s %s" % (src, dst, option))
        logging.info("Success to mount %s to %s" % (src, dst))

def umount_if_exist(src, dst):
    """ umount fs
    """
    result = os.popen("mount").readlines()
    mount = False
    for line in result:
        if src in line and dst in line:
            mount = True
            break
    if mount == False:
        logging.info("There is local fs")
    else:
        o = commands.getoutput("umount %s" % dst)
        if 'device is busy' in o:
            logging.error("failed umount %s as device is busy " % dst)
        else:
            logging.info("Success to umount %s" % dst)

def nfs_server_config(dir):
    """ configure nfs server
    """
    result = os.popen("service nfs status").readlines()
    for line in result:
        if "nfsd" in line and "stopped" in line:
            commands.getoutput("service nfs start")
            break
    commands.getoutput("exportfs -o rw,no_root_squash  localhost:%s" %dir)

def directory_setup(dict):
    """
    Setup directories and links needed by autotest
    """
    kvm_autotest_path = os.path.join(os.getcwd(),'kvm-test/tests/kvm')
    if dict.get("rhev") == "yes":
        kvm_autotest_root_path = '/data/images/kvm_autotest_root'
    else:
        kvm_autotest_root_path = '/home/kvm_autotest_root'

    qemu_link_path = os.path.join(kvm_autotest_path,"qemu")
    qemu_img_link_path = os.path.join(kvm_autotest_path,"qemu-img")
    image_link_path = os.path.join(kvm_autotest_path,"images")
    image_nfs_path = os.path.join(kvm_autotest_root_path,"images_nfs")
    iso_link_path = os.path.join(kvm_autotest_path,"isos")

    image_dir_path = os.path.join(kvm_autotest_root_path,"images")
    iso_dir_path = os.path.join(kvm_autotest_root_path,"iso")
    try:
        logging.info("prepare the directory and mount point ...")
        mkdir_if_not_exist(image_dir_path)
        mkdir_if_not_exist(iso_dir_path)
        mkdir_if_not_exist(image_nfs_path)
        logging.info("OK")

        logging.info("prepare the symlink required by autotest ...")
        link_if_not_exist('/usr/libexec/qemu-kvm','/usr/bin/qemu-kvm')
        link_if_not_exist('/usr/bin/qemu-kvm',qemu_link_path)
        link_if_not_exist('/usr/bin/qemu-img',qemu_img_link_path)
        link_if_not_exist(iso_dir_path,iso_link_path)
        if dict.get("use_storage") == "nfs":
            nfs_server_config(image_dir_path)
            op = "-o rw"
            src = "localhost:" + image_dir_path
            mount_if_not_exist(src,image_nfs_path, op)
            link(image_nfs_path,image_link_path)
        elif dict.get("use_storage") == "local":
            umount_if_exist(image_dir_path,image_nfs_path)
            link(image_dir_path,image_link_path)
        logging.info("OK")

        nfs_src = dict.get("nfs_src")
        op = "-o ro"
        mount_if_not_exist(nfs_src, iso_dir_path, op)
        mkdir_if_not_exist("/mnt/windows")
        mkdir_if_not_exist("/mnt/linux")
        mount_if_not_exist(dict.get("win_images"), "/mnt/windows", op)
        mount_if_not_exist(dict.get("linux_images"), "/mnt/linux", op)

        if dict.get("use_storage") == "iscsi":
            iscsi_params = ""
            logging.info("detecting iscsi logging ...")
            s, o = commands.getstatusoutput("iscsiadm -m session")
            if s == 0 and re.search("No active sessions", o) is None:
                logging.info("logout from iscsi target")
                for s in re.split("\n+", o):
                    # Get targetname and portal from session information
                    p, t = re.split('\s+', s)[-2:]
                    cmd = "iscsiadm -m node -T %s -p %s --logout" % (t, p)
                    s, o = commands.getstatusoutput(cmd)
                    logging.info("logged out from storage: %s" % o)

            logging.info("login to iscsi target")
            file('/etc/iscsi/initiatorname.iscsi', 'w').write(\
                 'InitiatorName=%s' % dict.get("iscsi_initiator"))
            s, o = commands.getstatusoutput("uname -r")
            if o.startswith("2.6.18"):
                s, o = commands.getstatusoutput("/etc/init.d/iscsid restart")
                if re.search("OK", o) is None:
                    logging.error("Fialed to restart iscsi service")
                    return False
            cmd = "iscsiadm -m discovery -t sendtargets -p %s" % \
                   dict.get("iscsi_server")
            s, o = commands.getstatusoutput(cmd)
            if s != 0:
                logging.error("Fialed to query from iscsi server")
                return False
            else:
                for i in re.split('\n+', o):
                    if re.search('%s' % dict.get("iscsi_keyword"), i)\
                       is not None:
                        iscsi_params = re.split('\s+', i)
            if iscsi_params == "":
                logging.error("Failed to find usable iscsi storage")
                return False
            cmd = "iscsiadm -m node -T %s -p %s --login" %\
                  (iscsi_params[1], iscsi_params[0])
            s , o = commands.getstatusoutput(cmd)
            if s != 0:
                logging.error("Fail to login iscsi storage")
                return False
            logging.info("Login to storage: %s" % o)

            time.sleep(1)
            # Get the main device name from partition information
            partitions = file("/proc/partitions").read()
            iscsi_dev_info = re.split('\n+', partitions)[-2]
            iscsi_dev = re.split('\s+', iscsi_dev_info)[-1]
            iscsi_dev = iscsi_dev[0:-len(re.findall('[0-9]', iscsi_dev))]
            dict["iscsi_number"] = len(re.findall(iscsi_dev, partitions)) - 1
            dict["iscsi_dev"] = os.path.join("/dev/", iscsi_dev)
            logging.info("OK")

    except OSError,message:
        msg =  "Directory Setup Failed!" + message
        logging.error(msg)
        return False

def stop_iptables():
    """
    Shutdown the iptables in the host.
    1) send 'service iptables stop' command

    """
    cmd = "service iptables stop"
    if os.system(cmd) != 0:
        logging.info("iptables has already stop")
    else:
        logging.info("Stop iptables succeeded")

def do_bridge_setup(bridge_name):
    """
    Do the setup of single bridge

    @param bridge_name: name of the bridge that'll be setup
    """
    if not bridge_name:
        message = "could not found bridge name in configuration file"
        logging.error(message)
        return False

    text = """#!/bin/sh
switch=%s
/sbin/ifconfig $1 0.0.0.0 up
/usr/sbin/brctl addif ${switch} $1
/usr/sbin/brctl setfd ${switch} 0
/usr/sbin/brctl stp ${switch} off
"""
    text = text % (bridge_name)
    kvm_dir = os.path.join(os.getcwd(), 'kvm-test/tests/kvm')
    qemu_ifup_file = os.path.join(kvm_dir, "scripts/qemu-ifup-%s" % bridge_name)
    f = open(qemu_ifup_file,"w")
    f.write(text)
    f.close()
    commands.getoutput('chmod a+x %s' % qemu_ifup_file)

def bridge_setup(dict):
    """
    prepare the qemu-ifup script which is used by TAP networking.
    1) get the bridge name from configuration file
    2) build the qemu-ifup-[bridge name] file in /etc

    @param dict: Dictionary with the test parameters
    """
    logging.info("prepare the qemu-ifup script")
    for i in dict.get('bridge_names').split():
        do_bridge_setup(i)
    logging.info("completing bridge setup")


def remote_machine_setup(dict):
    """
    Setup the remote machine environment for kvm testing.
    1) get the ip address of remote host.
    2) configure the nfs server of srchost and start it.
    3) create the require sym links and dirs require by autotest.
    4) copy the bridge up scripts to remote machine.

    @param dict: Dictionary with the test parameters
    """
    srchost = dict.get("srchost")
    dsthost = dict.get("dsthost")
    PASSWD = dict.get("hostpasswd")

    image_dir = os.path.join("kvm-test/tests/kvm","images")
    image_real_dir = os.path.realpath(image_dir)
    iso_dir = os.path.join("kvm-test/tests/kvm","isos")
    iso_real_dir = os.path.realpath(iso_dir)

    logging.info("source host %s destination host %s" % (srchost, dsthost))
    if dict.get("use_storage") == "local":
        if os.system("mount |grep -q %s\ on\ %s" % (os.path.join(
                      dict.get("nfs_storage")+":"+ dict.get("nfs_mntdir"),
                      srchost),
                      image_real_dir))==0:
            if os.system("umount %s" % image_real_dir)!=0:
                logging.info("Fail to umount %s" % image_real_dir)
        # setup local nfs, mount the dir from src host
        nfscmd = "echo '" + image_real_dir + \
                 " *(rw,no_root_squash)' > /etc/exports &&"
        nfscmd += "(service nfs restart && exportfs -a) > /dev/null"
        logging.info("setting up nfs mount dir on src host")
        if os.system(nfscmd):
            logging.error("setup nfs on source host failed")
            return False

    session = kvm_utils.ssh(dsthost, 22, "root", PASSWD, "#", timeout=30)
    if not session:
        logging.error("Fail to login to remote machine")
        return False
    else:
        session.set_status_test_command("echo $?")

    s = session.get_command_status("ln -s /usr/libexec/qemu-kvm /usr/bin/qemu-kvm")
    if s!=0 :
        logging.error("Fail to setup symlinks for remote machine")
        return False

    mkdir_image = "if [ ! -d " + image_real_dir + " ]; then mkdir -p " + \
                  image_real_dir + "; fi"
    mkdir_iso = "if [ ! -d " + iso_real_dir + " ]; then mkdir -p " + \
                iso_real_dir + "; fi"
    if session.get_command_status(mkdir_image) != 0:
        logging.error("Failed to make directory: %s" % image_real_dir)
        return False
    if session.get_command_status(mkdir_iso) != 0:
        logging.error("Failed to make directory: %s" % iso_real_dir)
        return False

    if dict.get("use_storage") == "nfs_storage":
        kvm_utils.nfs_mnt_img(dict, dict.get("nfs_storage") + ":"
                                           + dict.get("nfs_mntdir"),
                                           dict.get("nfs_localdir"))
        mntimage = "mount " + dict.get("nfs_storage") + ":" + \
                              dict.get("nfs_mntdir") + "/" +  \
                              srchost+ " "  + image_real_dir
    else:
        mntimage = "mount "+str(srchost)+":"+image_real_dir+" "+image_real_dir
    mntiso = "mount " + dict.get("nfs_src") + " " + iso_real_dir + " -o ro"

    def mount_dir(dir, cmd):
        mnt_srchost = cmd.split()[1].split(':')[0]
        if (dsthost == '0.0.0.0' or dsthost == srchost) and \
           (mnt_srchost == '0.0.0.0' or mnt_srchost == srchost):
            logging.info("No need to mount local directory to itself!")
            return

        if session.get_command_status("mount | grep %s\ on\ %s" %
                                             (cmd.split()[1], dir)) != 0:
            if session.get_command_status(cmd) != 0:
                logging.error("Fail to mount %s on remote machine" % dir)
                return False
            else:
                logging.info("%s mounted successfully!" % dir)
        else:
            logging.info("%s already mounted!" % dir)

    # Mount image dir
    mount_dir(image_real_dir, mntimage)
    mount_dir(iso_real_dir, mntiso)

    logging.info("build remote bridge scrips")
    ifupfile = "/etc/qemu-ifup-" + dict.get("bridge")
    if not kvm_utils.scp_to_remote(dsthost, 22, "root", PASSWD, ifupfile,
                                   "/etc/", timeout=300):
        logging.error("Fail to scp ifup scripts")
        return False
    else:
        logging.info("Bridge scripts ready")
    session.close()


def brewkoji_install():
    logging.info("querying the installation of brewkoji")
    s, o = commands.getstatusoutput("rpm -qa | grep brewkoji")
    if s != 0:
        if "el5" in commands.getoutput("uname -r"):
            cmd = "cp -f brew-rhel5.repo /etc/yum.repos.d"
        else:
            cmd = "cp -f brew-rhel6.repo /etc/yum.repos.d"
        s, o = commands.getstatusoutput(cmd)
        if s != 0:
            logging.error("could not copy the repo to /etc/yum.repos.d")
            return
        s, o = commands.getstatusoutput("yum install -y brewkoji")
        if s != 0:
            logging.error("Error found during brewkoji installation %s" % o)
            return
        logging.info("Installation finished")
    else:
        logging.info("Already installed")

