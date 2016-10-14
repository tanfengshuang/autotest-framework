import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID143284_list_available_service_levels(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:   
		#list available service levels
		service_level = ee().get_env(params)["servicelevel"]

		cmd="subscription-manager service-level --list"
		(ret,output)=eu().runcmd(session,cmd,"list available service levels")
		

	        if (ret == 0) and ("service_level" in output or "Service Levels" in output):      
           		logging.info("It's successful to list available service levels.")	
                else:
        	        raise error.TestFail("Test Failed - Failed to list available service levels.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list available service levels:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
