import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262188_return_exit_code_3_when_stop_rhsmcertd(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		# Check the exit code when rhsmcertd is running.
		ret, output = return_code_status(session)
		if ret == 0 and "is running" in output:
			logging.info("It's successful to check the exit code is 0 when rhsmcertd is running.")
		else:
			raise error.TestFail("Test Failed -failed to check the exit code is 0 when rhsmcertd is running.")

		# Check the exit code when rhsmcertd is stopped.
		stop_rhsmcertd(session)
		ret, output = return_code_status(session)
		if ret == 3 and "is stopped" in output:
			logging.info("It's successful to check the exit code is 3 when rhsmcertd is stopped.")
		else:
			raise error.TestFail("Test Failed -failed to check the exit code is 3 when rhsmcertd is stopped.")

		# Check the exit code when rhsmcertd is start
		start_rhsmcertd(session)
		ret, output = return_code_status(session)
		if ret == 0 and "is running" in output:
			logging.info("It's successful to check the exit code is 0 when rhsmcertd is started")
		else:
			raise error.TestFail("Test Failed - failed to check the exit code is 0 when rhsmcertd is started")
		
		# Check the exit code when rhsmcertd is restart
		restart_rhsmcertd(session)
		ret, output = return_code_status(session)
		if ret == 0 and "is running" in output:
			logging.info("It's successful to check the exit code is 0 when rhsmcertd is restarted")
		else:
			raise error.TestFail("Test Failed - failed to check the exit code is 0 when rhsmcertd is restarted")
			
		# Check the exit code after restart rhsmcertd then stop it
		stop_rhsmcertd(session)
		ret, output = return_code_status(session)
		if ret == 3 and "is stopped" in output:
			logging.info("It's successful to check the exit code is 3 when restart rhsmcertd then stop it")
		else:
			raise error.TestFail("Test Failed - failed to check the exit code is 3 when restart rhsmcertd then stop it")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to return_exit_code_3_when_stop_rhsmcertd:"+str(e))
		
	finally:
		start_rhsmcertd(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def return_code_status(session):
	cmd = "service rhsmcertd status"
	(ret,output)=eu().runcmd(session,cmd,"check exit code")
	return ret, output

def stop_rhsmcertd(session):
	cmd = "service rhsmcertd stop"
	(ret,output)=eu().runcmd(session,cmd,"stop rhsmcertd")
	if ret == 0 and "Stopping rhsmcertd..." in output:
		logging.info("It's successful to stop rhsmcertd")
	else:
		raise error.TestFail("Test Failed - failed to stop rhsmcertd")

def start_rhsmcertd(session):
	cmd = "service rhsmcertd start"
	(ret,output)=eu().runcmd(session,cmd,"start rhsmcertd")
	if ret == 0 and "Starting rhsmcertd..." in output:
		logging.info("It's successful to start rhsmcertd")
	else:
		raise error.TestFail("Test Failed - failed to start rhsmcertd")
		

def restart_rhsmcertd(session):
	cmd = "service rhsmcertd restart"
	(ret,output)=eu().runcmd(session,cmd,"restart rhsmcertd")
	if ret == 0 and "Stopping rhsmcertd..." in output and "Starting rhsmcertd..." in output:
		logging.info("It's successful to restart rhsmcertd")
	else:
		raise error.TestFail("Test Failed - failed to restart rhsmcertd")
		
	
