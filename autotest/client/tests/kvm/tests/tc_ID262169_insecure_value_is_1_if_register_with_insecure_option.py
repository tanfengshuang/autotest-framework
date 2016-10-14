import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262169_insecure_value_is_1_if_register_with_insecure_option(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
	
		#before register the insecure should be 0
		if not check_insecure(session):
			logging.info("It's successful to verify that the insecure should be 0 in rhsm.conf file before register with insecure option")
		else:
			raise error.TestFail("Test Failed - failed to verify that the insecure should be 0 in rhsm.conf file before register with insecure option")
		
		# register with insecure option
		cmd="subscription-manager register --username=%s --password=%s --insecure"%(username, password)
		(ret,output)=eu().runcmd(session,cmd,"register with insecure option")
		if ret == 0 and "The system has been registered with" in output:
			logging.info("It's successful to register with insecure option")
		else:
			raise error.TestFail("Test Failed - Failed to register with insecure option")
		
		#after register the insecure should be 1
		if check_insecure(session):
			logging.info("It's successful to verify that the insecure should be 1 in rhsm.conf file after register with insecure option")
		else:
			raise error.TestFail("Test Failed - failed to verify that the insecure should be 1 in rhsm.conf file after register with insecure option")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to verify that the insecure should be 1 in rhsm.conf file after register with insecure option:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def check_insecure(session):
	cmd="cat /etc/rhsm/rhsm.conf |grep insecure"
	(ret,output)=eu().runcmd(session,cmd,"check value of insecure")
	if ret == 0:
		logging.info("It's successful to check value of insecure")
		if "insecure = 1" in output:
			return 1
		elif "insecure = 0" in output:
			return 0
	else:
		raise error.TestFail("Test Failed - Failed to check value of insecure")
