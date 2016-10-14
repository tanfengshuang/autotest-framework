import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID155110_GUI_set_release_for_system(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_and_autosubscribe_in_gui(username, password)
		egu().click_preferences_menu()
		# list available releases
		guestname = params.get("guest_name")
		currentversion = eu().sub_getcurrentversion(session, guestname)
		egu().click_menu("system-preferences-dialog", currentversion.lower() + "-menu")
		egu().click_close_button()
		egu().click_preferences_menu()
		# check currentversion is in release version list. Since it's a menu in a dynamic combobox, so only check the menu exist.
		if egu().check_object_exist("system-preferences-dialog", "release-version-6server-combobox"):
			logging.info("It's successful to set_release_for_system.")
		else:
			raise error.TestFail("Test Faild - Failed to set_release_for_system!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to set_release_for_system:" + str(e))
	finally:
		egu().capture_image("set_release_for_system")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
