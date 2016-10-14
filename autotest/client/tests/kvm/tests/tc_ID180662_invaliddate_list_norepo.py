"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID180662_invaliddate_list_norepo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#auto subscribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#list consumed subscriptions
		installedproductname = ee().get_env(params)["installedproductname"]
		list_consumed_subscriptions(session,installedproductname)

		# List the repolist
		list_repolist(session)
		
		#Modify the system date to invalid date(after subscriptions' valid time)
		modify_systemtime_back(session)
		cmd="date -s 20150101"
		(ret, output) = eu().runcmd(session, cmd, "Modify the system date to after subscription valid time")    		
		if ret==0:
			logging.info(" It's successful to modify the system date to after subscription valid time.")				
		else:
			raise error.TestFail("Test Failed - Failed to modify the system date to after subscription valid time.")
			
		# List no repolist
		list_norepolist(session)
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list consumed subscriptions:"+str(e))
		
	finally:
		modify_systemtime_back(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


def list_consumed_subscriptions(session,installedproductname):
	cmd="subscription-manager list --consumed"
	(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")

	output_join = " ".join(x.strip() for x in output.split())
	if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
		logging.info("It's successful to list all consumed subscriptions.")
		return True
	else:
		raise error.TestFail("Test Failed - Failed to list all consumed subscriptions.")

def modify_systemtime_back(session):
	#Modify system time to current time
	cmd="hwclock --hctosys"
	(ret, output) = eu().runcmd(session, cmd, "Modify system time to current time")    

	if ret==0:
		logging.info(" It's successful to modify system time to current time.")
	else:
		raise error.TestFail("Test Failed - Failed to Modify system time to current time.")

def list_norepolist(session):
	# Check repolist is 0
	cmd ="yum clean all"
	(ret, output) = eu().runcmd(session, cmd, "Clean all repo") 
	cmd="yum repolist"
	(ret, output) = eu().runcmd(session, cmd, "List the repolist in the invalid time")    

	if "repolist: 0" in output :
		logging.info(" It's successful to list no repos in the invalid time.")
	else:
		raise error.TestFail("Test Failed - Failed to list no repos in the invalid time.")

def list_repolist(session):
	# List the repolist
	cmd ="yum clean all"
	(ret, output) = eu().runcmd(session, cmd, "Clean all repo") 
	cmd="yum repolist"
	(ret, output) = eu().runcmd(session, cmd, "List the repolist")    

	if "repolist: 0" not in output :
		logging.info(" It's successful to list repos .")
	else:
		raise error.TestFail("Test Failed - Failed to list repos.")
