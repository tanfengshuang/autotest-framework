import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262185_the_count_of_removed_subscription_after_import_cert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod=ee().get_env(params)["autosubprod"]
		
		# register and autosubscribe
		cmd="subscription-manager register --username=%s --password=%s --autosubscribe"%(username,password)
		(ret,output)=eu().runcmd(session,cmd,"register and auto-subscribe")
		if ret == 0:
			if ("The system has been registered with ID" in output) or ("The system has been registered with id" in output)\
                           and (autosubprod in output) and ("Subscribed" in output) and ("Not Subscribed" not in output):
				logging.info("It's successful to register and autosubscribe")
		else:
			raise error.TestFail("Test Failed - Failed to register and autosubscribe")
		
		# make cert (/root/cert.pem) to be imported
		path="/etc/pki/entitlement/"
		make_cert(session, path)
		
		# remove subscriptions
		cmd = "subscription-manager remove --all"
		(ret,output)=eu().runcmd(session,cmd,"remove all subscriptions")
		if ret ==0 and "1 subscription removed at the server." in output and "1 local certificate has been deleted" in output:
			logging.info("It's successful to remove all subscriptions")
		else:
			raise error.TestFail("Test Failed -failed to remove all subscriptions")
				
		# import cert
		cmd = "subscription-manager import --cert=/root/cert.pem"
		(ret,output)=eu().runcmd(session,cmd,"import cert")
		if ret == 0 and "Successfully imported certificate" in output:
			logging.info("It's successful to import cert")
		else:
			raise error.TestFail("Test Failed -failed to import cert")
			
		# remove subscriptions
		cmd = "subscription-manager remove --all"
		(ret,output)=eu().runcmd(session,cmd,"remove all subscriptions")
		if ret ==0 and "0 subscriptions removed at the server." in output and "1 local certificate has been deleted" in output:
			logging.info("It's successful to remove all subscriptions")
		else:
			raise error.TestFail("Test Failed -failed to remove all subscriptions")
		
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to remove all subscriptions:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def make_cert(session, path):
	# make cert
	path += "*"
	cmd="cat %s > /root/cert.pem"%path
	(ret,output)=eu().runcmd(session,cmd,"make cert")
	if ret==0:
		logging.info("It's successful to make cert")
	else:
		raise error.TestFail("Test Failed -failed to make cert")
