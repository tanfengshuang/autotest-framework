import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID155109_GUI_list_avaialble_release(test, params, env):

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
		cmd = "subscription-manager release --list"
		(ret, output) = eu().runcmd(session, cmd, "list available releases")
		if ret == 0 and currentversion in output:
			logging.info("It's successful to list available releases.")	
		else:
			raise error.TestFail("Test Failed - Failed to list available releases.")
		# check currentversion is in release version list. Since it's a menu in a dynamic combobox, so only check the menu exist.
		if egu().check_object_exist("system-preferences-dialog", currentversion.lower() + "-menu"):
			logging.info("It's successful to list avaialble release.")
		else:
			raise error.TestFail("Test Faild - Failed to list avaialble release!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to list avaialble release:" + str(e))
	finally:
		egu().capture_image("list_avaialble_release")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
