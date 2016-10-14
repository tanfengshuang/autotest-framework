import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190016_list_versioninfo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)

		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "subscription-manager version"
		(ret,output) = eu().runcmd(session, cmd, "list version info")
		if (ret == 0) and ('subscription management server' in output) and ('subscription-manager' in output) and ('python-rhsm' in output):
			resultoutput = output.splitlines()
			for lineoutput in resultoutput:
				tempoutput = lineoutput.strip().split(':')
				if (tempoutput[0].strip() == "server type" and tempoutput[1].strip() == "Red Hat Subscription Management") \
					or re.match('^[0-9]',tempoutput[1].strip()) is not None:
					pass
				else:
					raise error.TestFail("Test Failed - Failed to list the version of remote entitlment server.")
			logging.info("It's successful to list version info by running version command.")
		else:
			raise error.TestFail("Test Failed - Failed to list the version info by running version command.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to list the version info by running version command:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
