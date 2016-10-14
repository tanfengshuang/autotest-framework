import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID270213_check_system_cert_version(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "subscription-manager facts --list | grep cert"
		(ret,output) = eu().runcmd(session, cmd, "check system cert version")
		if ret == 0 and "system.certificate_version: 3.2" in output:
			logging.info("It's successful to check system cert version.")
		else:
			raise error.TestFail("Test Failed - Failed to check system cert version .")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check system cert version:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
