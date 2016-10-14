import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID143286_GUI_set_service_level(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_and_autosubscribe_in_gui(username, password)
		egu().click_preferences_menu()
		egu().click_menu("system-preferences-dialog", "premium-menu")
		egu().click_close_button()
		egu().click_preferences_menu()
		if egu().check_object_exist("system-preferences-dialog", "service-level-premium-combobox"):
			logging.info("It's successful to set_service_level.")
		else:
			raise error.TestFail("Test Faild - Failed to set_service_level!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to set_service_level:" + str(e))
	finally:
		egu().capture_image("set_service_level")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
