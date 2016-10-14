import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils,virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189594_servicelevel_name_insensitive(test,params,env):
	
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	
	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
	
		#list the designated service level
		servicelevel=ee().get_env(params)["servicelevel"]
		cmd="subscription-manager service-level --list"
		(ret,output)=eu().runcmd(session,cmd,"list correct service level")
		
		if ret == 0 and ("servicelevel" or "Service Levels" in output):
			logging.info("It's successful to list the service level %s."%servicelevel)
			
			#get a customized service level with lowercase and capital
			slabegin=servicelevel[:3].upper()
			slaend=servicelevel[3:].lower()
			servicelevel=slabegin+slaend
		
			cmd="subscription-manager service-level --set=%s"%servicelevel
			(ret,output)=eu().runcmd(session,cmd,"set a customized service level with lowercase and capital")
			if ret == 0 and "Service level set to: %s"%servicelevel in output:
				logging.info("It is successful to verify service level is insensitive to lowercase and capital.")
			else:
				raise error.TestFail("Test Failed - Failed to verify service level is insensitive to lowercase and capital.")
		else:
			raise error.TestFail("Test Failed - Failed to list the service level %s."%servicelevel)
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed -error happened when do test the service-level is insensitive to lowercase and capital:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
