import sys, os, subprocess, commands, random 
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190585_set_release(test, params, env):

	session,vm=eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		
	try:   
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)

		#auto-subscribe a subscription
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#list the subscription-manager release
		cmd = "subscription-manager release --list"
		(ret,output) = eu().runcmd(session, cmd, "list release info")

		#1. set list got from release list
		releaselist=ee().get_env(params)["releaselist"]
		outputtmp = output.strip().splitlines()
		if "+-" in outputtmp[0] and "+-" in outputtmp[2]:
			outputtmp.remove(outputtmp[0])
			outputtmp.remove(outputtmp[0])
			outputtmp.remove(outputtmp[0])
		#outputtmp = ','.join(output.strip().split('\n'))
		outputoneline = ','.join(outputtmp)

		print "outputoneline is %s"%outputoneline
		if ret == 0 and outputoneline == releaselist:
			#release_list = output.strip().splitlines()
			availrelease = random.sample(outputtmp, 1)[0]

			cmd="subscription-manager release --set=%s" %(availrelease)
			(ret,output)=eu().runcmd(session,cmd,"set a release from release list")
			if ret == 0 and "Release set to" in output:
				logging.info("It's successful to set a release from release list")
				
			else:
				raise error.TestFail("Test Failed - Failed to set a release from release list")
		else: 
			raise error.TestFail("Failed to check if release can be set correctly.")
			
		#2. set invalid release 
		invalidrelease='abc'
		cmd="subscription-manager release --set=%s" %(invalidrelease)
		(ret,output)=eu().runcmd(session,cmd,"set a invalid release")
		if ret!=0 and "No releases match" in output:
			logging.info("It's successful to check if invalid release can be set.")
		else:
			raise error.TestFail("Test Failed - Failed to check if invalid release can be set.")	
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check if release can be set correctly:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
