import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262156_rhsmcertd_status_is_3_if_the_program_not_running(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		#start rhsmcertd
		cmd = "service rhsmcertd start"
		(ret,output)=eu().runcmd(session,cmd,"start rhsmcertd")
		if ret == 0:
			logging.info("It's seccussful to start rhsmcertd")
		else:
			raise error.TestFail("Test Failed - failed to start rhsmcertd.")
		
		#check the status of rhsmcertd and return code
		cmd = "service rhsmcertd status"
		(ret,output)=eu().runcmd(session,cmd,"check the status of rhsmcertd")
		#if ret == 0 and "active (running)" in output:
		if ret == 0 and "running" in output:
			logging.info("It's successful to verify that the rhsmcertd status returns 0 when the program is running")
		else:
			raise TestFail("Test Failed - failed to check return code 0.")
			
		#stop rhsmcertd
		cmd = "service rhsmcertd stop"
		(ret,output)=eu().runcmd(session,cmd,"stop rhsmcertd")
		if ret == 0:
			logging.info("It's seccussful to stop rhsmcertd")
		else:
			raise error.TestFail("Test Failed - failed to stop rhsmcertd.")
			
		#check the the status of rhsmcertd
		cmd = "service rhsmcertd status"
		(ret,output)=eu().runcmd(session,cmd,"check the status of rhsmcertd")
		#if ret == 3 and "inactive (dead)" in output:
		if ret ==3 and "stopped" in output:
			logging.info("It's successful to verify that the rhsmcertd status returns 3 when the program is not running")
		else:
			raise TestFail("Test Failed - failed to check return code 3.")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened rhsmcertd_status_is_3_if_the_program_not_running:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
