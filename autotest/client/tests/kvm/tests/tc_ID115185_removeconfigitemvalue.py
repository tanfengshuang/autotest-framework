import sys, os, subprocess, commands, random, string
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

modinsecure = 1
modproxyport = 500

def run_tc_ID115185_removeconfigitemvalue(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
 		#[A] - prepare test env
		#modify values of configuration item for the system
#		cmd="subscription-manager config --server.insecure=%s --server.proxy_port=%s --rhsm.insecure=%s --rhsm.proxy_port=%s --rhsmcertd.insecure=%s --rhsmcertd.proxy_port=%s"%(modinsecure, modproxyport, modinsecure, modproxyport, modinsecure, modproxyport)
		cmd="subscription-manager config --server.insecure=%s --server.proxy_port=%s"%(modinsecure, modproxyport)
		(ret,output)=eu().runcmd(session,cmd,"modify values of config items")

		if (is_configuration_modified(session)): 
			logging.info("Default values of configuration items(insecure and proxy_port) have been modified.")

 		#[B] - run the test
		#remove values of configuration item for the system
	       # cmd="subscription-manager config --remove server.insecure --remove server.proxy_port --remove rhsm.insecure --remove rhsm.proxy_port --remove rhsmcertd.insecure --remove rhsmcertd.proxy_port"
	        cmd="subscription-manager config --remove server.insecure --remove server.proxy_port"
	        (ret,output)=eu().runcmd(session,cmd,"remove values of config items")

		if ret == 0 and "You have removed the value for section" in output and "The default value for" in output:
			if is_configuration_removed(session):
                		logging.info("It's successful to remove current values of configuration item for the system.")
			else: raise error.TestFail("Test Failed - remove current values of configuration item are not correct.")
		else: 
			raise error.TestFail("Failed to remove current values of configuration item.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do remove current values configuration info:"+str(e))
	finally:
		remove_current_config(session)	
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def get_system_configuration(session):
	cmd="subscription-manager config --list"
	(ret,output)=eu().runcmd(session,cmd,"get system configuration")
	if ret == 0:
		return output
	else : raise error.TestFail("Failed to List system configuration info.")

def is_configuration_modified(session):
	flag = False
	modified_config = get_system_configuration(session)
     	numsec = string.count(modified_config, 'insecure = %s'%modinsecure)
	numpp = string.count (modified_config, 'proxy_port = %s'%modproxyport)

       # if numsec == 3 and numpp == 3:
        if numsec == 1 and numpp == 1:
                flag = True

	return flag

def is_configuration_removed(session):
        flag = False
        removed_config = get_system_configuration(session)
        numsec = string.count(removed_config, 'insecure = [0]')
        numpp = string.count (removed_config, 'proxy_port = []')

        if numsec == 1 and numpp == 1:
                flag = True

        return flag


def remove_current_config(session):
        #remove modified value to default value
        #cmd="subscription-manager config --remove server.insecure --remove server.proxy_port --remove rhsm.insecure --remove rhsm.proxy_port --remove rhsmcertd.insecure --remove rhsmcertd.proxy_port"
        cmd="subscription-manager config --remove server.insecure --remove server.proxy_port"
        (ret,output)=eu().runcmd(session,cmd,"remove values of config items")

