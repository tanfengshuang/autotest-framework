import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID190632_GUI_quit_subscription_manager_from_menu(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().click_menu("main-window", "quit-menu")
		egu().wait_seconds(5)
		if not egu().check_object_exist("main-window","main-window"):
			logging.info("It's successful to check quit_subscription_manager_from_menu.")
		else:
			raise error.TestFail("Test Faild - Failed to check quit_subscription_manager_from_menu!")
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().click_my_subscriptions_tab()
		egu().sendkeys("<ctrl>", "q")
		egu().wait_seconds(5)
		if not egu().check_object_exist("main-window","main-window"):
			logging.info("It's successful to check quit_subscription_manager_from_menu.")
		else:
			raise error.TestFail("Test Faild - Failed to check quit_subscription_manager_from_menu!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check quit_subscription_manager_from_menu:" + str(e))
	finally:
		egu().capture_image("quit_subscription_manager_from_menu")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
