import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262260_check_repos_helpdoc(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "subscription-manager repos --help"
		helpout_enable = "repo to enable (can be specified more than once)"
		helpout_disable = "repo to disable (can be specified more than once)"
		helpout_wildcards = "Wildcards (* and ?) are supported."
				
		(ret,output) = eu().runcmd(session, cmd, "check the out put of subscription-manager repos help")
		if ret == 0 and helpout_enable in output and helpout_disable in output and helpout_wildcards in output:
			logging.info("It's successful to verify new features in rhsm repos help.")
		else:
			raise error.TestFail("Test Failed - Failed to verify new features in rhsm repos help.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to verify new features in rhsm repos help:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
