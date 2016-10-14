import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID327125_help_message_for_attach_servicelevel_should_be_in_sync_with_other_modules(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		# register 
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
		
		# attach and service-level help msg
		cmd = "subscription-manager attach --help | grep 'servicelevel' -A3"
		(ret,output) = eu().runcmd(session,cmd,"check help message for attach servicelevel")
		if ret == 0 and 'service level to apply to this system, requires --auto' in output:
			logging.info("It's successful to check help message for attach servicelevel")
		else:
			raise error.TestFail("Test Failed - Failed to check help message for attach servicelevel")
		
		# attach with pool and service level
		cmd = "subscription-manager attach --pool 8ac6a3a241bae96a0141baea35901305 --servicelevel premium"
		(ret,output) = eu().runcmd(session,cmd,"check help message for attach servicelevel")
		if ret != 0 and 'Error: Must use --auto with --servicelevel' in output:
			logging.info("It's successful to check attach with pool and service level")
		else:
			raise error.TestFail("Test Failed - Failed to check attach with pool and service level")
			
		# register and service-level help msg
		cmd = "subscription-manager register --help | grep servicelevel -A3"
		(ret,output) = eu().runcmd(session,cmd,"check register and service-level help msg")
		if ret == 0 and 'system preference used when subscribing automatically' in output and "requires --auto-attach" in output:
			logging.info("It's successful to check register and service-level help msg")
		else:
			raise error.TestFail("Test Failed - Failed to check register and service-level help msg")
		
		# service-level with org
		cmd = "subscription-manager service-level --org=admin"
		(ret,output) = eu().runcmd(session,cmd,"check service-level with org")
		if ret != 0 and 'Error: --org is only supported with the --list option' in output:
			logging.info("It's successful to check service-level with org")
		else:
			raise error.TestFail("Test Failed - Failed to check service-level with org")
		
		# service-level and org help
		cmd = "subscription-manager service-level --help | grep org -A3"
		(ret,output) = eu().runcmd(session,cmd,"check register and service-level help msg")
		if ret == 0 and 'specify an organization when listing available service' in output and "levels using the organization key, only used with" in output and "--list" in output:
			logging.info("It's successful to check service-level and org help")
		else:
			raise error.TestFail("Test Failed - Failed to check service-level and org help")
 
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when dependency on python-simplejson:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
