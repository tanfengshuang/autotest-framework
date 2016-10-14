import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262250_localize_rhsmgui_helpdoc(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "LANG=ru_RU.UTF-8 subscription-manager-gui --help"
		(ret,output) = eu().runcmd(session, cmd, "check if rhsmgui help doc localized")
		if ret == 0 and "Формат:" in output and "параметры:" in output:
			logging.info("It's successful to check if rhsmgui help doc localized.")
		else:
			raise error.TestFail("Test Failed - Failed to check if rhsmgui help doc localized.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check if rhsmgui help doc localized:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
