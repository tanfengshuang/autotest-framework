import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID284088_register_with_env_should_not_be_supported_in_sam(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:
		try:
			username = ee().get_env(params)["username"]
			password = ee().get_env(params)["password"]
			org = 'ACME_Corporation'
			cmd = "subscription-manager register --username=%s --password=%s --org=%s --env=Library"%(username, password, org)
			(ret, output) = eu().runcmd(session, cmd, "register with environments")
			if ret != 0 and "Error: Server does not support environments." in output:
				logging.info("It's successful to verify that register_with_env_should_not_be_supported_in_sam")
			else:
				raise error.TestFail("Test Failed - failed to verify that register_with_env_should_not_be_supported_in_sam")
		except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when register_with_env:" + str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

