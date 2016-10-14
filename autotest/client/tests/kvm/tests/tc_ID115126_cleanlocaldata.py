import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115126_cleanlocaldata(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password) 		
 		
 		#[A] - prepare test env
		
		#get uuid of consumer
		cmd="subscription-manager identity | grep identity"
		(ret,output)=eu().runcmd(session,cmd,"")
		uuid=output.split(':')[1].strip()
               
		#get env variables
		productid=ee().get_env(params)["productid"]
		#prepare a env auto subsribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#[B] - run the test
		#clean local consumer and subscription data
		cmd = "subscription-manager clean"
		(ret, output) = eu().runcmd(session, cmd, "clean local data")

		if ret == 0 and ("All local data removed" in output):
			cmd1 = 'ls /etc/pki/consumer/'
			cmd2 = 'ls /etc/pki/entitlement/'
			(ret1, output1) = eu().runcmd(session, cmd1, "list what's in the consumer folder")
			(ret2, output2) = eu().runcmd(session, cmd2, "list what's in the entitlement folder")
			if ret1 == 0 and output1 == '' and ret2 == 0 and output2 == '':
				logging.info("It's successful to clean local consumer and entitlement information")
			else:
				raise error.TestFail("Test Failed - The information shows that it's failed to clean local data.")
		else:
			raise error.TestFail("Test Failed - The information shows that it's failed to clean local data---return code or output is wrong.")

			
			####old scripts for rhel5 rhel6
			#cmd = "ls /etc/pki/"
			#(ret, output) = eu().runcmd(session, cmd, "list what's in the pki folder")
			#if ret == 0 and "entitlement" not in output and "consumer" not in output:
			#	logging.info("It's successful to clean local consumer register information.")
			#	
			#	#(1)
			#	if eu().sub_isregistered(session):
			#		raise error.TestFail("Test Failed - The information shows that it's failed to clean local consumer register information.")
			#	else:
			#		logging.info("It's successful to clean local consumer register information to make system unregister.")
			#	#(2)
			#	cmd="subscription-manager list --consumed"
			#	(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")
			#	guest_name=params.get("guest_name")			
			#	if "6.3" in guest_name or "5.9" in guest_name or "5.10" in guest_name or "6.4" in guest_name:
			#		expectedstr = "No consumed subscription pools to list" 
			#	else:
			#		expectedstr = "No Consumed subscription pools to list"
#
#				if expectedstr in output:
#					logging.info("It's successful to clean all local subscription data.")
#				else:
#					raise error.TestFail("Test Failed - The information shows that it's failed to clean all local subscription data.") 
#
#				#re-register with consumerid for cleaning test environment later
#				cmd="subscription-manager register --consumerid=%s --username=%s  --password=%s"%(uuid,username,password)
#				(ret,output)=eu().runcmd(session,cmd,"register with consumerid")				
#			else:
#				raise error.TestFail("Test Failed - The information shows that it's failed to clean local consumer register information.")		
#		else:
#			raise error.TestFail("Test Failed - The information shows that it's failed to clean local consumer register information.")
      
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do clean local consumer and subscription data:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
