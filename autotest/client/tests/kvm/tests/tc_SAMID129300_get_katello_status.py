import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129300_get_katello_status(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#Get the status of the katello server
		cmd="headpin -u admin -p admin ping"
		(ret,output)=eu().runcmd(session,cmd,"get katello server status")

		if (ret == 0) and ("candlepin_auth" in output) and ("elasticsearch" in output) and ("katello_jobs" in output):
			logging.info("It's successful to get katello server status.")
		else:
			raise error.TestFail("It's failed to get katello server status.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when ping katello server:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
