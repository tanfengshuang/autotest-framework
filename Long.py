##@ Summary: Virtlab wrapper for unstable.py
##@ Description: 
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:    
##@ Version:    1

import os, sys, commands, getopt
import logging

if __name__ == "__main__":

    # Build dict from argv
    dict = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', ['mail_list=','test_cmd=','subject='])
    except getopt.GetoptError:
        logging.info("Unexpected args")
        sys.exit(1)

    for item in opts:
        dict[item[0][2:]] = item[1]

    logging.info("Remove the svn repo produced by virtlab")
    try:
        commands.getstatusoutput("rm -rf autotest")
        commands.getstatusoutput("rm -rf staf-kvm-devel")
    except:
        pass

    logging.info("Detecting the installation of git")
    s, o = commands.getstatusoutput("git --version")
    if s != 0:
        logging.info("Installating git")
        s, o = commands.getstatusoutput("yum install -y git-core")
        if s != 0:
            logging.info(o)
            logging.info("Fail to install git")
            sys.exit(1)

    logging.info("Cloning staf-kvm-devel")
    s, o = commands.getstatusoutput("git clone "
                                   "git://10.66.82.200/staf-kvm-devel")
    if s != 0:
        logging.info(o)
        logging.info("Fail to clone staf-kvm-devel")

    logging.info("Cloning autotest")
    s, o = commands.getstatusoutput("git clone "
                                    "git://10.66.82.200/autotest")
    if s != 0:
        logging.info(o)
        logging.info("Fail to clone autotest")

    # Do the symlinks
    logging.info("Prepare the symlinks")
    autotest_path = os.path.join(os.getcwd(), "autotest")
    staf_kvm_path = os.path.join(os.getcwd(), "staf-kvm-devel")
    client_path = os.path.join(autotest_path, "client")
    os.symlink(client_path , os.path.join(staf_kvm_path, "kvm-test"))
    
    # Get the params
    mail_list = dict.get("mail_list", "jasowang@redhat.com")
    test_cmd = dict.get("test_cmd",
                        "python ConfigLoop.py --category=unstable_loop --guestname=all --platform=64")
    subject = dict.get("subject", "Long-time-run")
    
    command = "python unstable.py \'%s\' \'%s\' \'%s\' \'%s\' \'%s\' \'%s\'" % \
              (staf_kvm_path, autotest_path, test_cmd, mail_list, "git pull", subject)

    print "test command is %s" % command
    while True:
        if os.system(command):
            sys.exit(1)
    
    
    
    
