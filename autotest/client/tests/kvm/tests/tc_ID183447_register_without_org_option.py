'''
@author          :soliu@redhat.com
@date            :2013-03-12
'''
import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID183447_register_without_org_option(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register a system
		eu().sub_unregister(session)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]

		cmd_register_without_org_option="subscription-manager register --username=%s --password=%s" %(username, password)
		#step1:display the orgs available for a user
		(ret, output)=eu().runcmd(session, cmd_register_without_org_option, "subscription-manager register without org option")
		if ret == 0:
			if "The system has been registered with id" in output:
				logging.info("It is successful to rigster without org option!")
			else:
				raise error.TestFail("Failed to register without org option!")


	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when register without org option"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
