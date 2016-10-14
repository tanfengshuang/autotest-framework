import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190589_run_identity_when_not_registered(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#use identity command to show where system is registerd to
		cmd="subscription-manager identity"
		(ret,output)=eu().runcmd(session,cmd,"running identity command")
		if ret != 0 and ("This system is not yet registered. Try 'subscription-manager register --help' for more information." in output):
			logging.info("It's successful to check the output of identity command when the machine is not registered.")
		else:
			raise error.TestFail("Test Failed - Failed to check the output of identity command when the machine is not registered.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the output of identity command when the machin is not registered:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

