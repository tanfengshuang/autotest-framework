import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID284092_register_without_env_in_sam(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:
		try:
			username = ee().get_env(params)["username"]
			password = ee().get_env(params)["password"]
			org = 'ACME_Corporation'
			cmd = "subscription-manager register --username=%s --password=%s --org=%s"%(username, password, org)
			(ret, output) = eu().runcmd(session, cmd, "register without environments")
			if ret == 0 and ("The system has been registered with ID" in output or "The system has been registered with id" in output):
				logging.info("It's successful to verify that sam support registration without environments")
			else:
				raise error.TestFail("Test Failed - failed to verify that sam support registration without environments")
		except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when register_with_env:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

