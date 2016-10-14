import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262178_remind_message_after_disable_manage_repos(test, params, env):

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
		
		# enable manage_repos in rhsm.conf
		set_manage_repos(session, "1")
		
		# list known repos
		ret, output =list_known_repos(session)
		if ret == 0 and "Available Repositories in /etc/yum.repos.d/redhat.repo" in output and "Enabled:1" in output:
			logging.info("It's successful to display the known repos")
		else:
			raise error.TestFail("Test Failed -failed to display the known repos")
				
		# disable manage_repos in rhsm.conf
		set_manage_repos(session, "0")
		
		# list known repos
		ret, output =list_known_repos(session)
		if ret == 0 and "Repositories disabled by configuration." in output:
			logging.info("It's successful to display the remind message")
		else:
			raise error.TestFail("Test Failed -failed to display the remind message")
		
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to display the remind message:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def set_manage_repos(session, val):
	cmd="subscription-manager config --rhsm.manage_repos=%s"%val
	(ret,output)=eu().runcmd(session,cmd,"set manage_repos value")
	if ret == 0:
		logging.info("It's successful to set manage_repos value")
	else:
		raise error.TestFail("Test Failed - Failed to set manage_repos value")
		
def list_known_repos(session):
	cmd="subscription-manager repos --list | head -7"
	(ret,output)=eu().runcmd(session,cmd,"set manage_repos value")
	return ret, output
