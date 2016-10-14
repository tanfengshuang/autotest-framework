"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID181268_import_valid_invaild_cert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#get env variables
		autosubprod = ee().get_env(params)["autosubprod"]
		installedproductname = ee().get_env(params)["installedproductname"]
						
		#create invaild pem file
		cmd="touch /root/invalid.pem"
		(ret, output) = eu().runcmd(session, cmd, "create invalid pem file")    
		if ret==0:
			logging.info(" It's successful to create invalid pem file.")				
		else:
			raise error.TestFail("Test Failed - Failed to create invalied pem file.")
			
		#create vaild pem file
		eu().sub_autosubscribe(session, autosubprod)
		cmd="cat /etc/pki/entitlement/*-key.pem /etc/pki/entitlement/*.pem > /root/valid.pem"	
		(ret,output)=eu().runcmd(session,cmd,"Create valid pem file")			
		if ret == 0 :
			logging.info("It's successful to create valid cert file.")
		else:
			raise error.TestFail("Test Failed - Failed to create valid cert file.")
		
		#Unsubscribe all product
		cmd = "subscription-manager unsubscribe --all"
		(ret,output)=eu().runcmd(session,cmd,"Unsubscribe all products")
		if ret == 0 :
			list_noconsumed_subscriptions(session)
		else :
			raise error.TestFail("Test Failed - Failed to unsubscribe all product.")
			
		#Import more two certificates
		cmd="subscription-manager import --certificate=/root/valid.pem --certificate=/root/invalid.pem"
		(ret,output)=eu().runcmd(session,cmd,"import valid and invalid pem files")

		if ("Successfully" in output) and ("not a valid certificate file" in output):
			logging.info("It's successful to check import two certificates.")
		else:
			raise error.TestFail("Test Failed - Failed to check import two certificates.")
		
		# Check the import result
		list_consumed_subscriptions(session,installedproductname)
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check import more than one entitlement certificate:"+str(e))
		
	finally:
		remove_certfile(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Runnidng Test Case: %s ==========="%__name__)


def list_noconsumed_subscriptions(session):
	cmd="subscription-manager list --consumed"
	(ret,output)=eu().runcmd(session,cmd,"no consumed subscriptions in list")

	output_join = " ".join(x.strip() for x in output.split())
	if ret == 0 and (("No consumed" in output) or ("No consumed" in output_join)):
		logging.info("It's successful to check no consumed subscriptions.")
		return True
	else:
		raise error.TestFail("Test Failed - Failed to check no consumed subscriptions.")
		return False

def list_consumed_subscriptions(session,installedproductname):
	cmd="subscription-manager list --consumed"
	(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")

	output_join = " ".join(x.strip() for x in output.split())
	if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
		logging.info("It's successful to list all consumed subscriptions.")
		return True
	else:
		raise error.TestFail("Test Failed - Failed to list all consumed subscriptions.")
		return False

def remove_certfile(session):
	cmd="rm -rf /root/*.pem"
	(ret,output)=eu().runcmd(session,cmd,"Remove all pem file under /root")
	if ret == 0 :
		logging.info("It's successful to remove all pem file under /root.")
		return True
	else:
		raise error.TestFail("Test Failed - Failed to Remove all pem file under /root.")
		return False	
