import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262163_autosubscribe_with_force_after_registered(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		#register
		eu().sub_register(session, username, password)
		
		# get the first consumer id
		consumer_id1=eu().sub_get_consumerid(session)
		
		# remove rhsm.log
		remove_file(session, '/var/log/rhsm/rhsm.log')
		
		#autosubscribe with --force
		cmd = "subscription-manager register --username=%s --password=%s --force --autosubscribe"%(username, password)
		(ret,output2)=eu().runcmd(session,cmd,"autosubscribe with --force")
		if ret == 0:
			# check if there are errors in rhsm.log
			check_error_in_file(session, '/var/log/rhsm/rhsm.log')
			
			# get the second consumer id
			consumer_id2=eu().sub_get_consumerid(session)
			out1="The system with UUID %s has been unregistered"%consumer_id1
			out2="The system has been registered with ID: %s"%consumer_id2 
			if (out1 in output2) and (out2 in output2) and "Status:Subscribed" in output2:
				logging.info("It's successful to autosubscribe with --force")
			else:
				raise error.TestFail("Test Failed - Failed to autosubscribe with --force")
		else:
				raise error.TestFail("Test Failed - Failed to autosubscribe with --force, the return code is non-zero")
		
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe with --force:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def remove_file(session, filename):
	cmd = "rm -f %s"%filename
	(ret,output)=eu().runcmd(session,cmd,"remove file")
	if ret == 0:
		logging.info("It's successful to Delete file %s."%filename)
	else:
		raise error.TestFail("Test Failed - Failed to Delete file %s."%filename)

def check_error_in_file(session, filename):
	cmd = "grep 'Traceback' %s"%filename
	(ret,output)=eu().runcmd(session,cmd,"check error in file")
	if ret != 0:
		logging.info("It's successful to verify that there is no error in file %s"%filename)
	else:
		raise error.TestFail("TestFailed - Failed to verify if there are errors in file %s"%filename)

	
