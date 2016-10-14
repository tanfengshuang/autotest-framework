import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189938_config_cmd_default_to_list(test, params, env):
	
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" %__name__)
	
	try:
		#run cmd with config only
		cmd = "subscription-manager config"
		(ret, output) = eu().runcmd(session, cmd, "running config without option")
		configout = output
		
		#run cmd with config --list
		cmd = "subscription-manager config --list"
		(ret, output) = eu().runcmd(session, cmd, "running config with option --list")
		configlistout = output
	
		if configout == configlistout:
			logging.info("It's successful to verify config cmd with list option by default - the output of both config and config --list is the same.")
		else:
			raise error.TestFail("Test Failed - Failed to verify config cmd with list option by default - the output of both config and config --list is not the same.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to verify config cmd with list option by default:" + str(e))
	finally:
		logging.info("========== End of Running Test Case: %s ==========" %__name__)
