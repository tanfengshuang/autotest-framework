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

def run_tc_ID181220_import_invaild_cert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
		
		#create invaild pem file
		cmd="touch /root/testinvalid.pem"
		(ret, output) = eu().runcmd(session, cmd, "create invalid pem file")    
		if ret==0:
			logging.info(" It's successful to create invalid pem file.")
		else:
			raise error.TestFail("Test Failed - Failed to create invalied pem file.")

		#import the invaild pem file
		cmd="subscription-manager import --certificate=/root/testinvalid.pem"
		(ret,output)=eu().runcmd(session,cmd,"import invalid pem file")

		if ret != 0 and "not a valid certificate file" in output:
			logging.info("It's successful to check import invalid cert file.")
		else:
			raise error.TestFail("Test Failed - Failed to check import invalid cert file.")
			
		#list consumed subscriptions
		cmd="subscription-manager list --consumed"
		(ret, output) = eu().runcmd(session, cmd, "list consumed subscriptions")  
		
		if (ret == 0) and ("No consumed subscription pools" in output):
			logging.info("It's successful to check consumed subscriptions.")
		else:
			raise error.TestFail("Test Failed - Failed to check consumed subscriptions.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check import invalid certificate:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Runnidng Test Case: %s ==========="%__name__)
