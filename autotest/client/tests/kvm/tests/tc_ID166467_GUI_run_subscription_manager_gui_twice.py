import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID166467_GUI_run_subscription_manager_gui_twice(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		cmd = "subscription-manager-gui & \ ; sleep 20"
		(ret, output) = eu().runcmd(session, cmd, "run subscription-manager-gui the first time")
		if ret == 0:
			logging.info("It's successful to run subscription-manager-gui the first time.")
		else:
			raise error.TestFail("Test Failed - Failed to run subscription-manager-gui the first time")
		# open subscription - manager - gui
# 		egu().open_subscription_manager(session)
# 		if egu().check_window_open("main-window"):
# 			logging.info("It's successful to check subscription-manager-gui opened.")
# 		else:
# 			raise error.TestFail("Test Faild - Failed to check subscription-manager-gui opened!")
		cmd = "subscription-manager-gui"
		(ret, output) = eu().runcmd(session, cmd, "check message when run_subscription_manager_gui_twice")
		if ret == 0 and "subscription-manager-gui is already running" in output :
			logging.info("It's successful to check message when run_subscription_manager_gui_twice.")
		else:
			raise error.TestFail("Test Failed - Failed to check message when run_subscription_manager_gui_twice")

# 		cmd = "nohup subscription-manager-gui > /tmp/subscription-manager-gui.log 2>&1 &"
# 		(ret, output) = eu().runcmd(session, cmd, "run subscription-manager-gui the second time")
# 		if ret == 0 and "[2]" in output :
# 			cmd = "cat /tmp/subscription-manager-gui.log"
# 			(ret, output) = eu().runcmd(session, cmd, "check message when run_subscription_manager_gui_twice")
# 			if ret == 0 and "subscription-manager-gui is already running" in output :
# 				logging.info("It's successful to check message when run_subscription_manager_gui_twice.")
# 			else:
# 				raise error.TestFail("Test Failed - Failed to check message when run_subscription_manager_gui_twice")
# 		else:
# 			raise error.TestFail("Test Failed - Failed to run subscription-manager-gui the second time")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to run_subscription_manager_gui_twice:" + str(e))
	finally:
		egu().capture_image("run_subscription_manager_gui_twice")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
