import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID330289_request_for_list_consumed_field_subscription_type(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		#register the system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
		
		# list available subscriptions and check the subscription type
		cmd = "subscription-manager list --available | grep 'Subscription Type'| sort | uniq"
		(ret,output)=eu().runcmd(session,cmd,"check the subscription type for list available")
		if ret == 0 and "Subscription Type:" in output:
			logging.info("It's successful to check the subscription type for list available.") 
		else:
			raise error.TestFail("Test Failed - Failed to check the subscription type for list available.")
		
		# auto-attach
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		# list consumed subscriptions and check the subscription type
		cmd = " subscription-manager list --consumed | grep 'Subscription Type'| sort | uniq"
		(ret,output)=eu().runcmd(session,cmd,"check the subscription type for list consumed")
		if ret == 0 and "Subscription Type:" in output:
			logging.info("It's successful to check the subscription type for list consumed.") 
		else:
			raise error.TestFail("Test Failed - Failed to check the subscription type for list consumed.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the subscription type:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
