import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID143280_autosubscribe_with_multiple_SLAs(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)
	
	try:
		#[A] - prepare test env
		#get service_level
		service_level = ee().get_env(params)["servicelevel"]

                #[B] - run the test		
		# auto subscribe with one service level
		cmd="subscription-manager subscribe --auto --servicelevel=%s" %service_level
		(ret,output)=eu().runcmd(session,cmd,"autosubscribe with one service-level")

		if ret == 0 and ("Status:Subscribed" in output) or re.search("Status:\s+Subscribed", output):
			logging.info("It's successful to do autosubscribe with one service-level: %s."%service_level)
		else:
			raise error.TestFail("Test Failed - Failed to auto subscribe with one service level.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto subscribe with one service level:"+str(e))

	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


