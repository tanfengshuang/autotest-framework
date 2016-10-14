import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189600_set_wrong_servicelevel(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#set a wrong service level such as notreal
		cmd="subscription-manager service-level --set=notreal"
		(ret,output)=eu().runcmd(session,cmd,"set a wrong service level")

		if ret != 0 and "Service level 'notreal' is not available to units of organization " in output:      
			logging.info("It's successful to check the error message when set a wrong service level.")
		else:
			raise error.TestFail("Test Failed - Failed to check the error message when set a wrong service level.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the error message when set a wrong service level:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
