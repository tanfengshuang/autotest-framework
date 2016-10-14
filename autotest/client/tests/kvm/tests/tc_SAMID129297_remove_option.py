import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129297_remove_option(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#save a option
		optionname="option_name1"
		optionvalue="option_value1"
		eu().sam_save_option(session, optionname, optionvalue)

		#remove the option
		eu().sam_remove_option(session, optionname)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when save a option:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

