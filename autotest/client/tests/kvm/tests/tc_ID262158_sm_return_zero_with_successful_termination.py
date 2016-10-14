import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262158_sm_return_zero_with_successful_termination(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		#verify with 'susbcription-manager --help'
		cmd = "subscription-manager --help"
		(ret,output)=eu().runcmd(session,cmd,"sm --help")
		if ret == 0:
			logging.info("It's seccussful to verify that sm_return_zero_with_successful_termination with 'susbcription-manager --help' !")
		else:
			raise error.TestFail("Test Failed - failed to verify that sm_return_zero_with_successful_termination with 'susbcription-manager --help' !.")
		
		#verify with ' rct --help'
		cmd = "rct --help"
		if ret == 0:
			logging.info("It's seccussful to verify that sm_return_zero_with_successful_termination with 'rct --help' !")
		else:
			raise error.TestFail("Test Failed - failed to verify that sm_return_zero_with_successful_termination with 'rct --help' !.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to verify that sm_return_zero_with_successful_termination:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
