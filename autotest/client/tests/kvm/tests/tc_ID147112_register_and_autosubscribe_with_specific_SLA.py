import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID147112_register_and_autosubscribe_with_specific_SLA(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #get username and password
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	
	try:
		#[A] - prepare test env
		#get service_level
		service_level = ee().get_env(params)["servicelevel"]

		#[B] - run the test		
		# register and auto subscribe with one service level
		cmd="subscription-manager register --username=%s --password=%s --autosubscribe --servicelevel=%s" %(username, password, service_level)
		(ret,output)=eu().runcmd(session,cmd,"register and autosubscribe with one specific service-level")

		if ret == 0 and (("The system has been registered with ID" in output) or ("The system has been registered with id" in output)) and \
			(("Status:Subscribed" in output) or re.search("Status:\s+Subscribed", output)):
			logging.info("It's successful to do register and autosubscribe with one service-level: %s."%service_level)
		else:
			raise error.TestFail("Test Failed - Failed to register and auto subscribe with one service level.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do register and subscribe with one service level:"+str(e))

	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


