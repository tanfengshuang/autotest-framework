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

def run_tc_ID180681_autosubscribe_failed(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		samip=params.get("samhostip")
		#Modify the system date to invalid date(after subscriptions' valid time)
		modify_systemtime_back(session, samip)
		cmd="date -s 20280101"
		(ret, output) = eu().runcmd(session, cmd, "Modify the system date to subscription invalid time")
		if ret==0:
			logging.info("It's successful to set all subscriptions to be not compatible by changing client system time.")
		else:
			raise error.TestFail("Test Failed - Failed to set all subscriptions to be no compatible by changing server system time.")
			
		(ret, output)=eu().runcmd_remote(samip, 'root', 'redhat', cmd)
		if ret == 0:
			logging.info("It's successful to set all subscriptions to be not compatible by changing server system time.")
		else:
			raise error.TestFail("Test Failed - Failed to set all subscriptions to be no compatible by changing server system time.")

		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#auto subscribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		sub_noautosubscribe(session, autosubprod)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do check autosubscribe with no compatible subscription:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		modify_systemtime_back(session, samip)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_noautosubscribe(session, autosubprod):
	cmd="subscription-manager subscribe --auto"
	(ret, output)=eu().runcmd(session, cmd, "autosubscribe with no compatible subscription")

	if ret != 0:
		if (autosubprod in output) and ("Not Subscribed" in output):
			logging.info("It's successful to check autosubscribe with no compatible subscription.")
		else:
			raise error.TestFail("Test Failed - Failed to check autosubscribe with no compatible subscription.")
	else:
		raise error.TestFail("Test Failed - Failed to check hasn't auto-subscribe.")

def modify_systemtime_back(session, samip):
	#Modify system time to current time
	cmd="hwclock --hctosys"
	(ret, output) = eu().runcmd(session, cmd, "Modify system time to current time")    

	if ret==0:
		logging.info("It's successful to modify client system time to current time.")
	else:
		raise error.TestFail("Test Failed - Failed to Modify system time to current time.")
		
	(ret, output)=eu().runcmd_remote(samip, 'root','redhat', cmd)
	if ret==0:
		logging.info("It's successful to modify server system time to current time.")
	else:
		raise error.TestFail("Test Failed -Failed to recover the server system time")
