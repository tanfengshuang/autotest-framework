import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262215_list_versioninfo_before_register(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		unregisterinfo = "server type: This system is currently not registered."
		cmd = "subscription-manager version"
		(ret,output) = eu().runcmd(session, cmd, "list version info")
		if (ret == 0) and (unregisterinfo in output):
			logging.info("It's successful to list version info by running version command before register.")
		else:
			raise error.TestFail("Test Failed - Failed to list the version info by running version command before register.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to list the version info before register by running version command:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
