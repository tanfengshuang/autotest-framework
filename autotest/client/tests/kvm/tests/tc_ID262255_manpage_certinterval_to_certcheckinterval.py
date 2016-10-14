import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262255_manpage_certinterval_to_certcheckinterval(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "man -P cat rhsmcertd | grep cert-interval"
		(ret,output) = eu().runcmd(session, cmd, "find cert-interval in man page")
		if ret == 1 and output == "":
			logging.info("It's successful to verify no cert-interval in man page.")
		else:
			raise error.TestFail("Test Failed - Failed to verify no cert-interval in man page .")
			
		cmd = "man -P cat rhsmcertd | grep cert-check-interval"
		(ret,output) = eu().runcmd(session, cmd, "find cert-check-interval in man page")
		if ret == 0 and output != "":
			logging.info("It's successful to verify cert-check-interval in man page.")
		else:
			raise error.TestFail("Test Failed - Failed to verify cert-check-interval in man page .")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to run a unknow cmd with rhsm:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
