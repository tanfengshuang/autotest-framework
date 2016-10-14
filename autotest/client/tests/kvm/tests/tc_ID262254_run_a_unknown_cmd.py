import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262254_run_a_unknown_cmd(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "subscription-manager fool"
		(ret,output) = eu().runcmd(session, cmd, "run a unknow command")
		if ret == 1:
			logging.info("It's successful to run a unknow cmd with rhsm.")
		else:
			raise error.TestFail("Test Failed - Failed to run a unknow cmd with rhsm.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to run a unknow cmd with rhsm:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
