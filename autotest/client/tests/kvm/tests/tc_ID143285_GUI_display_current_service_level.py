import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID143285_GUI_display_current_service_level(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_and_autosubscribe_in_gui(username, password)
		egu().click_preferences_menu()
		# get service-level by cmd line
		cmd = "subscription-manager service-level --show"
		(result, output) = eu().runcmd(session, cmd, "display current service-level")
		if result == 0:
			if "Service level preference not set" in output:
				service_level = "service-level-notset-combobox"
			elif "Current service level:" in output:
				service_level = "service-level-" + output.split(":")[1].strip().lower() + "-combobox"
			logging.info("It's successful to get current service level by cmd: %s." % service_level)
		else:
			raise error.TestFail("Test Failed - Failed to get current service level by cmd.")

		if egu().check_object_exist("system-preferences-dialog", service_level):
			logging.info("It's successful to display current service level.")
		else:
			raise error.TestFail("Test Faild - Failed to display current service level!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to display current service level:" + str(e))
	finally:
		egu().capture_image("display_current_service_level")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
