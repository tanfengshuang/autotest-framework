import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID327124_man_page_entry_for_status_option_needs_to_be_edited(test, params, env):
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		cmd='man subscription-manager | grep "subscription-manager status" -A5'
		(ret,output)=eu().runcmd(session,cmd,"man page entry for status option")
		if ret == 0 and "Overall Status: Current" in output:
			logging.info("It's successful to check man page entry for status option.") 
		else:
			raise error.TestFail("Test Failed - Failed to check man page entry for status option.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check man page entry for status option:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
