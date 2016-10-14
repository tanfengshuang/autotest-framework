import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID217501_GUI_open_rhsm_after_change_hostname(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		tmp_hostname = "hostname-temp"
		bak_hostname = ""
		cmd = "hostname"
		(ret, output) = eu().runcmd(session, cmd, "get hostname in order to restore it")
		if ret == 0:
			bak_hostname = output
			logging.info("It's successful to get old hostname %s." % bak_hostname)
		else:
			raise error.TestFail("Test Failed - Failed to get old hostname")

		cmd = "hostname %s" % tmp_hostname
		(ret, output) = eu().runcmd(session, cmd, "change hostname to %s." % tmp_hostname)
		if ret == 0:
			logging.info("It's successful to change hostname to %s." % tmp_hostname)
		else:
			raise error.TestFail("Test Failed - Failed to change hostname to %s." % tmp_hostname)

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		if egu().check_window_open("main-window"):
			logging.info("It's successful to open rhsm gui after change hostname")
		else:
			raise error.TestFail("Test Faild - Failed to open rhsm gui after change hostname")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when open rhsm gui after change hostname:" + str(e))
	finally:
		egu().capture_image("check_rhsm_gui_open_succeed")
		cmd = "hostname %s" % bak_hostname
		(ret, output) = eu().runcmd(session, cmd, "restore hostname to %s." % bak_hostname)
		if ret == 0:
			logging.info("It's successful to restore hostname to %s." % bak_hostname)
		else:
			raise error.TestFail("Test Failed - Failed to restore hostname to %s." % tmp_hostname)
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
