import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID310812_autoattach_presist_servicelevel_setting(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		
		cmd = "subscription-manager attach --auto --servicelevel="
		(ret, output) = eu().runcmd(session, cmd, "auto-subscribe")
		
		servicemess = "Service level set to:"
		
		if ret == 0 and (servicemess in output) and ("Subscribed" in output) \
			and ("Not Subscribed" not in output):
			logging.info("It's successful to auto-subscribe and set the service level to none.")
		else:
			raise error.TestFail("Test Failed - Failed to auto-subscribe and set the service level to none.")
	
		cmd = "subscription-manager service-level"
		(ret, output) = eu().runcmd(session, cmd, "service level list")
		
		servicelist = "Service level preference not set"
		
		if ret == 0 and (servicelist in output):
			logging.info("It's successful to list service level is none.")
		else:
			raise error.TestFail("Test Failed - Failed to list service level is none.")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list products and subscriptions:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
