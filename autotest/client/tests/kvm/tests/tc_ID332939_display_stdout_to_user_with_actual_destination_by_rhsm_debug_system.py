import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID332939_display_stdout_to_user_with_actual_destination_by_rhsm_debug_system(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		# register the client
		eu().sub_register(session,username,password)
		
		#execute rhsm-debug system
		cmd = "rhsm-debug system"
		(ret,output) = eu().runcmd(session,cmd,"execute rhsm-debug system")
		if ret == 0 and "Wrote: /tmp/rhsm-debug-system" in output:
			check_rhsm_debug_system_output(session, output)
			logging.info("It's successful to display stdout to user with actual destination by rhsm debug system")
		else:
			raise error.TestFail("Test Failed - display stdout to user with actual destination by rhsm debug system.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check config options:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def check_rhsm_debug_system_output(session, output):
	debug_result=output.split(":")[1].strip()
	cmd = "ls %s"%debug_result
	(ret,output) = eu().runcmd(session,cmd,"check rhsm-debug system result")
	if ret == 0 and debug_result in output:
		logging.info("It's successful to list rhsm debug system result: %s"%debug_result)
	else:
		raise error.TestFail("Test Failed - Failed to list rhsm debug system result.")

