import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189936_facts_cmd_default_to_list(test, params, env):
	
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" %__name__)
	
	try:
		#run cmd with facts only
		cmd = "subscription-manager facts"
		(ret, output) = eu().runcmd(session, cmd, "running facts without option")
		factsout = output
		
		#run cmd with facts --list
		cmd = "subscription-manager facts --list"
		(ret, output) = eu().runcmd(session, cmd, "running facts with option: --list")
		factslistout = output
	
		if factsout == factslistout:
			logging.info("It's successfull to check the default output of repos: the output of facts is the same as facts --list!")
		else:
			raise error.TestFail("Test Faild - It's failed to check the default output of repos: the output of facts is not the same as facts --list!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the default output of facts cmd:" + str(e))
	finally:
		logging.info("========== End of Running Test Case: %s ==========" %__name__)