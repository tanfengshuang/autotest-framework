import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID332567_Need_Description_for_rhsm_debug_system_option(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		# Check the description of rhsm-debug MODULE-NAME
		cmd = "rhsm-debug --help | grep system"
		(ret,output)=eu().runcmd(session,cmd,"check man page for repo-override")
		if ret == 0 and "Assemble system information as a tar file or directory" in output:
			logging.info("It's successful to Check the description of rhsm-debug MODULE-NAME.") 
		else:
			raise error.TestFail("Test Failed - Failed to Check the description of rhsm-debug MODULE-NAME.")		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the subscription type:"+str(e))
		
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
