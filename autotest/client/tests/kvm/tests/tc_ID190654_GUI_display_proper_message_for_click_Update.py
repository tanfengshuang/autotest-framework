import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID190654_GUI_display_proper_message_for_click_Update(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_in_gui(username, password)
		egu().click_all_available_subscriptions_tab()
		if egu().check_object_exist("main-window", "search-subscriptions-hint-label") :
			logging.info("It's successful to check display_proper_message_for_click_Update")
		else:
			raise error.TestFail("Test Faild - Failed to check display_proper_message_for_click_Update")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check display_proper_message_for_click_Update:" + str(e))
	finally:
		egu().capture_image("display_proper_message_for_click_Update")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
