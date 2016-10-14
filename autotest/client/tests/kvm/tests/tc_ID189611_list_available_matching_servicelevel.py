import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189611_list_available_matching_servicelevel(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:   
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		#get service_level
		service_level = ee().get_env(params)["servicelevel"]

		#list available subscriptions matching specified service level
		cmd = "subscription-manager list --available --servicelevel=%s" % service_level
		(ret, output) = eu().runcmd(session, cmd, "list available subscriptions matching specified service level")

		if ret == 0:
			logging.info("It's successful to list available subscriptions matching specified service level.")

			if check_servicelevel_in_listavailable_ouput(output, service_level):
				logging.info("It's successful to check specified service level in the ouput of listing available subscriptions.")   
			else:
				raise error.TestFail("Test Failed - Failed to check specified service level in the ouput of listing available subscriptions.")
		else:
			raise error.TestFail("Test Failed - Failed to list available subscriptions matching specified service level.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when listing available subscriptions matching specified service level:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)
        
def check_servicelevel_in_listavailable_ouput(output, service_level):
	if "No available subscription pools to list" not in output:
		pool_list = eu().parse_listavailable_output(output)
		for item in pool_list:
			if (item['ServiceLevel']).lower() != (service_level).lower():
				return False
			else:
				continue
		return True
	else:
		logging.info("There is no available subscription pools to list!")
		return False
