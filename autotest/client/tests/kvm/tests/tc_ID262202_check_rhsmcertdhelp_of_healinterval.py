import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262202_check_rhsmcertdhelp_of_healinterval(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "rhsmcertd --help | grep heal-interval"
		helpout = "deprecated, see --auto-attach-interval"
		(ret,output) = eu().runcmd(session, cmd, "check the out put of rhsmcertd help")
		if ret == 0 and helpout in output:
			logging.info("It's successful to verify --auto-attach-interval in rhsmcertd help.")
		else:
			raise error.TestFail("Test Failed - Failed to verify --auto-attach-interval in rhsmcertd help. .")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check --auto-attach-interval in rhsmcertd help.:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
