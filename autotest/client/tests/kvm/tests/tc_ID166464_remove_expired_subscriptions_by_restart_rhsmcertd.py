import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID166464_remove_expired_subscriptions_by_restart_rhsmcertd(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

    #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	samip=params['samhostip']

	try:
		# register and auto-attach
		eu().sub_register(session,username,password)
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		# Check the subscription status
		sub_status = get_subscription_status(session)
		if sub_status == "True":
			logging.info("It's successful to check the subscription status is not expired")
		else:
			raise error.TestFail("Test Failed - Failed to check the subscription status is not expired.")
		
		# set the system times later than 12 years.
		cmd = "date -d '+12 years'"
		specified_time = get_specified_time(session, cmd)
		cmd = "date -s '%s'"%(specified_time)
		set_system_time(session, cmd)
		
		#restart rhsmcertd service
		cmd='service rhsmcertd restart'
		eu().runcmd(session,cmd,"restart rhsmcertd service")
		logging.info('sleep 120 second for waiting rhsmcertd service...') 
		time.sleep(120)
		
		# Check the subscription status
		sub_status = get_subscription_status(session)
		if sub_status == "False":
			logging.info("It's successful to check the subscription status is expired")
		else:
			raise error.TestFail("Test Failed - Failed to check the subscription status is expired.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto-subscribe:"+str(e))
	finally:
		# recover the system times
		cmd='hwclock --hctosys'
		(ret,output)=eu().runcmd(session,cmd,"restore the client system time")
		if ret == 0:
			logging.info("It's successful to restore client system time")
		else:
			raise error.TestFail("Test Failed - Failed to restore client system time.")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

   
def get_specified_time(session, cmd):
	(ret,output)=eu().runcmd(session,cmd,"get_specified_time")
	if ret == 0:
		logging.info("It's successful to get_specified_time")
		specified_time=output.strip()
		return specified_time
	else:
		raise error.TestFail("Test Failed - Failed to get_specified_time.")
		

def set_system_time(session, cmd):
	(ret,output)=eu().runcmd(session,cmd,"set client time with specified time")
	if ret == 0:
		logging.info("It's successful to set/recover client time with specified time")
	else:
		raise error.TestFail("Test Failed - Failed to set/recover client time with specified time.")
		
def get_subscription_status(session):
	cmd = "subscription-manager list --consumed | grep Active"
	(ret,output)=eu().runcmd(session,cmd,"get subscription status")
	if ret == 0:
		if "False" in output:
			logging.info("It's successful to get subscription status: the subscription is expired")
			return "False"
		elif "True" in output:
			logging.info("It's successful to get subscription status: the subscription is not expired")
			return "True"
	else:
		raise error.TestFail("Test Failed - Failed to get subscription status.")

