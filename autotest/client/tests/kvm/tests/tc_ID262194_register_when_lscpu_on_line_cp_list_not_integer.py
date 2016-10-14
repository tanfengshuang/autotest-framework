import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262194_register_when_lscpu_on_line_cp_list_not_integer(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		# Register
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		# Change the lscpu.on-line_cpu(s)_list to a not integer number.
		change_facts(session)
		
		# update the system facts to make change effect.
		update_facts(session)
		
		# Register from subscription-manager with correct username and password after change facts
		cmd="subscription-manager register --username=%s --password=%s --force"%(username, password)
		(ret,output)=eu().runcmd(session,cmd,"register after change facts")
		if ret == 0 and "The system has been registered with" in output:
			logging.info("It's successful to register after change facts")
		else:
			raise error.TestFail("Test Failed - Failed to register after change facts")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to return_exit_code_3_when_stop_rhsmcertd:"+str(e))
		
	finally:
		restore_facts(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def change_facts(session):
	cmd = "echo \'{\"lscpu.on-line_cpu(s)_list\" : \"1.8\"}\' > /etc/rhsm/facts/custom.facts"
	(ret,output)=eu().runcmd(session,cmd,"check exit code")
	if ret == 0:
		logging.info("It's successful to change the lscpu.on-line_cpu(s)_list to non-integer")
	else:
		raise error.TestFail("Test Failed - failed to change the lscpu.on-line_cpu(s)_list to non-integer")

def update_facts(session):
	cmd = "subscription-manager facts --update"
	(ret,output)=eu().runcmd(session,cmd,"update facts")
	if ret == 0 and "Successfully updated the system facts." in output:
		logging.info("It's successful to update facts")
	else:
		raise error.TestFail("Test Failed - failed to update facts")

def restore_facts(session):
	cmd = "rm -f /etc/rhsm/facts/custom.facts"
	(ret,output)=eu().runcmd(session,cmd,"restore facts")
	if ret == 0:
		logging.info("It's successful to restore facts")
	else:
		raise error.TestFail("Test Failed - failed to restore facts")
