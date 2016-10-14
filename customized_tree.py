##@ Summary: Import the test result from local execution or autotest server
##@ Description:
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:
##@ Version:    1

import os, sys, commands, getopt, re
import wrapper,logging

if __name__ == "__main__":

    # Build dict from argv
    dict = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], '',
                                   ['tree=',"cmd="])
    except getopt.GetoptError:
        logging.info("Unexpected args")
        sys.exit(1)

    for item in opts:
        dict[item[0][2:]] = item[1]

    tree = dict.get('tree')
    cmd = re.findall("--cmd=(.*)$", ' '.join(sys.argv))[0]

    if not tree:
        sys.exit(1)

    git_cmd = "wget http://kernel.org/pub/software/scm/git/git-1.7.3.3.tar.bz2 \
           && tar xvfj git-1.7.3.3.tar.bz2 && cd git-1.7.3.3 && ./configure \
           && make && make install"
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.info("Installing Git ...")
        commands.getstatusoutput(git_cmd)
    s, o = commands.getstatusoutput("git --help")
    if s != 0:
        logging.error("Git is not installed!")
        sys.exit(1)

    logging.info("Probing the virtlab mount point ...")
    mounts = file("/proc/mounts").read()
    result_dir = os.path.join(os.path.realpath('kvm-test'), 'results')
    autotest_dir = result_dir.split('/')[-3]
    virtlab_nfs_dir = re.findall("(.*)\s+%s" % result_dir, mounts, re.M)[0]
    logging.info("Virtlab nfs dir %s" % mounts)

    logging.info("Umount the result dir ...")
    s, o = commands.getstatusoutput("umount %s" % result_dir)
    if s != 0:
        logging.error("Could not umount %s:%s" % (result_dir, o))
        sys.exit(1)

    logging.info("Removing the original tree address")
    s, o = commands.getstatusoutput("rm -rf %s " % autotest_dir)
    if s != 0:
        logging.error("Could not remove the tree %s" % o)
        sys.exit(1)

    logging.info("Cloning tree: git clone %s" % tree)
    s, o = commands.getstatusoutput("git clone %s %s" % (tree, autotest_dir))
    if s != 0:
        logging.error("Could not finish the cloning:%s" % o)
        sys.exit(1)

    logging.info("Create result directory")
    s, o = commands.getstatusoutput("mkdir -p %s" % result_dir)
    if s != 0:
        logging.error("Could not create directory")
        sys.exit(1)

    logging.info("Remount the virtlab dir")
    s, o = commands.getstatusoutput("mount %s %s" % (virtlab_nfs_dir, result_dir))
    if s != 0:
        logging.error("Could not mount %s to %s: %s" % (virtlab_nfs_dir, result_dir, o))
        sys.exit(1)

    logging.info("Executing the command %s" % cmd)
    os.system(cmd)

