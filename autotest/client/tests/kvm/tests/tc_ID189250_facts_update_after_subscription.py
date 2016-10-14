'''
@author            :soliu@redhat.com
@date              :2013-03-12
'''
import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189250_facts_update_after_subscription(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register a system
                username=ee().get_env(params)["username"]
                password=ee().get_env(params)["password"]
                eu().sub_register(session, username, password, "")

		cmd_system_entitlement="subscription-manager facts --list|grep system.entitlement"
		#step1:check its value of system.entitlements
		(ret, output)=eu().runcmd(session, cmd_system_entitlement, "list system entilement")
		if ret == 0:
			if "system.entitlements_valid: invalid" in output:
				logging.info("It is successful to check the value of system.entitlement after register!")
			else:
				raise error.TestFail("Failed to check the value of system.entitlement after register!")

		#step2:auto-subscribe
		autosubprod = ee().get_env(params)["autosubprod"]
                eu().sub_autosubscribe(session, autosubprod)

		#step3:re-check the value of system.entitlements_valid
		(ret, output)=eu().runcmd(session, cmd_system_entitlement, "list system entilement")
                if ret == 0:
                        if "system.entitlements_valid: valid" in output:
                                logging.info("It is successful to test facts update after subscription!")
                        else:
                                raise error.TestFail("Failed to test facts update after subscription!")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when test facts update after subscription"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
