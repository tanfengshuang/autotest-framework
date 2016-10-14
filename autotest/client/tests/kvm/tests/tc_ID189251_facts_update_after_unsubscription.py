'''
@author           :soliu@redhat.com
@date             :2013-03-12
'''
import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189251_facts_update_after_unsubscription(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register a system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session, username, password, "")
		#auto-subscribe
		autosubprod = ee().get_env(params)["autosubprod"]
                eu().sub_autosubscribe(session, autosubprod)
		
		#step1:check the value of system.entitlements_valid
		cmd_system_entitlement="subscription-manager facts --list|grep system.entitlement"
		(ret, output)=eu().runcmd(session, cmd_system_entitlement, "list system entilement")
		if ret == 0:
			if "system.entitlements_valid: valid" in output:
				logging.info("It is successful to check the value of system.entitlements after consume product!")
			else:
				raise error.TestFail("Failed to check the value of system.entitlements after consume product!")

		#step2:un-subscribe all products
		eu().sub_unsubscribe(session)

		#step3:re-check the value of system.entitlements_valid
		(ret, output)=eu().runcmd(session, cmd_system_entitlement, "list system entilement")
                if ret == 0:
                        if "system.entitlements_valid: invalid" in output:
                                logging.info("It is successful to test the facts update after unsubscription!")
                        else:
                                raise error.TestFail("Failed to test the facts update after unsubscription!")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when test the facts update after unsubscription"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
