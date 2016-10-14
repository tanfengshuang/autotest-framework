import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189602_clear_current_servicelevel(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#get service_level
		service_level = ee().get_env(params)["servicelevel"]

		#(1)Test 1: with --set=\"\" option
		#set service-level as precondition
		eu().sub_set_servicelevel(session, service_level)

		#clear current service level by subscription-manager service-level --set=""
		cmd="subscription-manager service-level --set=\"\""
		(ret,output)=eu().runcmd(session,cmd,"clear current service level with --set=\"\" option")

		if ret == 0 and "Service level preference has been unset" in output:	  
			logging.info("It's successful to clear current service level with --set=\"\" option.")	
		else:
			raise error.TestFail("Test Failed - Failed to clear current service level with --set=\"\" option.")

		#(2)Test 2: with --unset option	
		#set service-level as precondition
		eu().sub_set_servicelevel(session, service_level)

		#clear current service level by subscription-manager service-level --unset
		cmd="subscription-manager service-level --unset"
		(ret,output)=eu().runcmd(session,cmd,"clear current service level with --unset option")
		
		if ret == 0 and "Service level preference has been unset" in output:	  
			logging.info("It's successful to clear current service level with --unset option.")	
		else:
			raise error.TestFail("Test Failed - Failed to clear current service level with --unset option.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to clear current service level:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
