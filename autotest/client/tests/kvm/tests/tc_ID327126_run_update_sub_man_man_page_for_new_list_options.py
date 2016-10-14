import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID327126_run_update_sub_man_man_page_for_new_list_options(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		cmd='subscription-manager list --available --help | egrep "no-overlap|match-installed" -A1'
		(ret,output)=eu().runcmd(session,cmd,"check subscription-manager man page for new list options")
		if ret == 0 and "shows pools which provide products that are not" in output and "already covered; only used with --available" in output \
		and "shows only subscriptions matching products that are" in output and "currently installed; only used with --available" in output:
			logging.info("It's successful to check subscription-manager man page for new list options.") 
		else:
			raise error.TestFail("Test Failed - Failed to check subscription-manager man page for new list options.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check subscription-manager man page for new list options:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
