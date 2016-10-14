import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID324080_config_should_NOT_have_proxy_options(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		cmd = "subscription-manager config --help | grep -A1 -- --proxy"
		(ret,output) = eu().runcmd(session,cmd,"check proxy option")
		if ret != 0 and 'proxy' not in output:
			logging.info("It's successful to check config should NOT have proxy options")
		else:
			raise error.TestFail("Test Failed - Failed to check config should NOT have proxy options.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check config options:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

