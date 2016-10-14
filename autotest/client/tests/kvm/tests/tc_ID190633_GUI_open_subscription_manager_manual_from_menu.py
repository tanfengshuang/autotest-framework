import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID190633_GUI_open_subscription_manager_manual_from_menu(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().click_gettingstarted_menu()
		if egu().check_object_exist("subscription-manager-manual-window", "subscription-manager-manual-window"):
			logging.info("It's successful to check open_subscription_manager_manual_from_menu.")
		else:
			raise error.TestFail("Test Faild - Failed to check open_subscription_manager_manual_from_menu!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check open_subscription_manager_manual_from_menu:" + str(e))
	finally:
		egu().capture_image("open_subscription_manager_manual_from_menu")
		egu().close_window("subscription-manager-manual-window")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
