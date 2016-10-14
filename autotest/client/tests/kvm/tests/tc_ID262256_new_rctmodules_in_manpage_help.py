import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262256_new_rctmodules_in_manpage_help(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "rct --help"
		(ret,output) = eu().runcmd(session, cmd, "find cert-interval in man page")
		if ret == 0 and "cat-manifest" in output and "dump-manifest" in output:
			logging.info("It's successful to verify new modules in help doc.")
		else:
			raise error.TestFail("Test Failed - Failed to verify new modules in help doc .")
			
		cmd = "man -P cat rct | grep cat-manifest"
		(ret,output) = eu().runcmd(session, cmd, "find cat-manifest in man page")
		if ret == 0 and output != "":
			logging.info("It's successful to verify cat-manifest in man page.")
		else:
			raise error.TestFail("Test Failed - Failed to verify cat-manifest in man page .")
			
		cmd = "man -P cat rct | grep dump-manifest"
		(ret,output) = eu().runcmd(session, cmd, "find dump-manifest in man page")
		if ret == 0 and output != "":
			logging.info("It's successful to verify dump-manifest in man page.")
		else:
			raise error.TestFail("Test Failed - Failed to verify dump-manifest in man page .")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check new modules in the manpage and help doc:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
