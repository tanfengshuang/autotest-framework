import sys, os, subprocess, commands, logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268204_compliance_of_unregistered_system(test, params, env):

	try:
		session, vm = eu().init_session_vm(params, env)
		logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

		# register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		eu().check_product_status(session, "Not Subscribed")
		eu().check_product_status_details(session, "Not covered by a valid subscription")
		eu().check_status_overall(session, "Invalid")

		# autosubscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		eu().check_product_status(session, "Subscribed")
		eu().check_product_status_details(session, "")
		eu().check_status_overall(session, "Current")

		eu().sub_unregister(session)
		eu().check_product_status(session, "Unknown")
		eu().check_product_status_details(session, "")
		eu().check_status_overall(session, "Unknown")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check compliance_of_unregistered_system:" + str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)
