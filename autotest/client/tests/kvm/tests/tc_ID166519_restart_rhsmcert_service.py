import sys, os, subprocess, commands, random, re, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID166519_restart_rhsmcert_service(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	
	try:
		#get username and password
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
	
		autosubprod = ee().get_env(params)["autosubprod"]
        #auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)
		
		#set healfrequency = 1
		sub_set_healfrequency(session, 1)
			
		#1. Unsubscribe the subscription
		eu().sub_unsubscribe(session)

		#2. refresh the local data
		cmd='subscription-manager refresh'
		(ret,output)=eu().runcmd(session, cmd, "reflash")
		
		if ret == 0  and 'All local data refreshed' in output:	
			logging.info("It's successful to do refresh local data")
		else:
			raise error.TestFail("Test Failed - Failed to do refresh.")

		#3. Restart the rhsmcertd service
		cmd='service rhsmcertd restart'
		eu().runcmd(session, cmd, "restart rhsmcertd")

		#4. List the consumed
		cmd='subscription-manager refresh'
		(ret,output)=eu().runcmd(session,cmd,"refresh rhsmcertd")
		
		logging.info("Waiting 90 seconds for rhsmcertd service to take effect...")
		time.sleep(90)
		
		if eu().sub_isconsumed(session, autosubprod):
			logging.info("It's successful to list consumed.")
		else:
			raise error.TestFail("Test Failed - Failed to list consumed.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do restart rhsmcertd service :"+str(e))

	finally:
		sub_set_healfrequency(session, 1440)
		cmd='service rhsmcertd restart'
		eu().runcmd(session, cmd, "restart rhsmcertd")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_set_healfrequency(session, frtime):
	
	cmd = "subscription-manager config --rhsmcertd.healfrequency=%s" %frtime
	cmd510 = "subscription-manager config --rhsmcertd.autoattachinterval=%s" %frtime
	(ret, output) = eu().runcmd(session, cmd, "set healfrequency")

	if ret == 0:
		logging.info("It successful to set healfrequency")
	else:
		(ret, output) = eu().runcmd(session, cmd510, "set autoattachinterval")
		if ret == 0:
			logging.info("It successful to set autoattachinterval")
		else:
			logging.error("Test Failed - Failed to set healfrequency or autoattachinterval.")
