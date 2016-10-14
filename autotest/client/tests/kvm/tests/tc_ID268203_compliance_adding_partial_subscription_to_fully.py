import sys, os, subprocess, commands, logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268203_compliance_adding_partial_subscription_to_fully(test, params, env):

	try:
		session, vm = eu().init_session_vm(params, env)
		logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)
	
		# register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		# remove all product certs
		eu().clear_product_cert(session)

		# add product cert
		eu().add_product_cert(session, "37060.pem")
		
		# remove product cert
		eu().remove_product_cert(session, "37060.pem")
		
		# autosubscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
	
		# check product is fully compliant
		cmd = "subscription-manager status"
		(ret, output) = eu().runcmd(session, cmd, "check product status")
####		if ret == 0 and "Insufficient" in output :
			logging.info("It's successful to verify that product is fully compliant")
		else:
			raise error.TestFail("Test Failed - failed to verify that product is fully compliant")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check compliance_adding_partial_subscription_to_fully:" + str(e))
	finally:
		eu().sub_unregister(session)
		# remove all product certs
		eu().clear_product_cert(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)
