import sys, os, subprocess, commands, random, time, logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268182_healing_of_core_based_subscription(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:
		session, vm = eu().init_session_vm(params, env)
		logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

		# register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		# set healFrequency = 2
		
		
		# need core based subscription that can be autoheal, or add pem to product
		
		# restart rhsmcertd service
		eu().restart_rhsmcertd()
		time.sleep(120)


	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when healing_of_core_based_subscription:" + str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

