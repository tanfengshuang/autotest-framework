import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262271_disable_package_reporting(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "cat /etc/rhsm/rhsm.conf | grep report_package_profile"
				
		(ret,output) = eu().runcmd(session, cmd, "check the report_package_profile in the config file")
		if ret == 0 and output:
			logging.info("It's successful to check the report_package_profile in the config file.")
		else:
			raise error.TestFail("Test Failed - Failed to check report_package_profile in the config file.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check report_package_profile in the config file:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
