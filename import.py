##@ Summary: Import the test result from local execution or autotest server
##@ Description: 
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:    
##@ Version:    1

import os, sys, commands, getopt
import logging

client_dir = os.path.realpath('kvm-test')
sys.path.insert(0, client_dir)
import setup_modules
setup_modules.setup(base_path=client_dir,
                    root_module_name="autotest_lib.client")
sys.path.pop(0)

from autotest_lib.client.common_lib import utils

sys.path.insert(0, os.path.join(os.getcwd(), 'kvm-test/virt'))
import common, virt_utils
sys.path.pop(0)

if __name__ == "__main__":

    # Build dict from argv
    dict = {}
    try:
        opts, args = getopt.getopt(sys.argv[1:], '',
                                   ['host=','remote_path=','passwd=','user='])
    except getopt.GetoptError:
        logging.info("Unexpected args")
        sys.exit(1)
        
    for item in opts:
        dict[item[0][2:]] = item[1]

    path = dict.get("remote_path")
    passwd = dict.get("passwd")
    user = dict.get("user")
    host = dict.get("host")
    local_path = os.path.join(os.getcwd(),"kvm-test/")
    remote_path = os.path.join(path, "client/results")

    scp_cmd = "scp -r %s@%s:%s %s" % (user, host, remote_path, local_path)
    logging.info("command is %s" % scp_cmd)
    try:
       virt_utils.scp_from_remote(host, 22, user, passwd, remote_path,
                                       local_path)
    except Exception, e:
        logging.error("Copying failed with output: %s" %e)
        sys.exit(1)
    else:
        logging.info("Importing finished.")

    
