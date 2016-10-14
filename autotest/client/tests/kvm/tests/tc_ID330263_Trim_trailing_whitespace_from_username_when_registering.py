import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID330263_Trim_trailing_whitespace_from_username_when_registering(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		# register with space on the back of username
		username1 = username + ' '
		cmd = "subscription-manager register --force --username='%s' --password=%s"%(username1, password)
		(ret,output)=eu().runcmd(session,cmd,"register with space on the back of username")
		if ret == 0 and "The system has been registered with ID" in output:
			logging.info("It's successful to with space on the back of username.") 
		else:
			raise error.TestFail("Test Failed - Failed to with space on the back of username.")
		
		# register with space on the front of username
		username2 = ' ' + username
		cmd = "subscription-manager register --force --username='%s' --password=%s"%(username2, password)
		(ret,output)=eu().runcmd(session,cmd,"register with space on the front of username")
		if ret == 0 and "The system has been registered with ID" in output:
			logging.info("It's successful to with space on the back of username.") 
		else:
			raise error.TestFail("Test Failed - Failed to with space on the front of username.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the subscription type:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
