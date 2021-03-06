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

def run_tc_ID180401_unsubscribe_with_wrong_serial_number(test, params, env):

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
		
		#Unsubscribe the consumed subscription via the serial number
		cmd="subscription-manager unsubscribe --serial=1234567890"
		(ret, output) = eu().runcmd(session, cmd, "Unsubscribe the consumed subscription via the wrong cert serial number")

		if (ret != 0) and ("could not be found" in output) and ("unsuccessfully removed" in output):
			logging.info("It's successful to check Unsubscribe the consumed subscription via the wrong cert serial number")
		else:
			raise error.TestFail("Test Failed - Failed to check Unsubscribe the consumed subscription via the wrong cert serial number")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when to check Unsubscribe the consumed subscription via the wrong cert serial number:"+str(e))
		
	finally:
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
