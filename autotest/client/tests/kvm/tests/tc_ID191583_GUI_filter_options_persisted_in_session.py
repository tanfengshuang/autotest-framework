import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID191583_GUI_filter_options_persisted_in_session(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_in_gui(username, password)
		egu().click_all_available_subscriptions_tab()
		egu().click_filters_button()
		egu().check_checkbox("filter-options-window", "match-installed-checkbox")
		egu().uncheck_checkbox("filter-options-window", "match-system-checkbox")
		egu().uncheck_checkbox("filter-options-window", "do-not-overlap-checkbox")
		egu().click_filter_close_button()
		egu().click_filters_button()
		if not (egu().verifycheck_checkbox("filter-options-window", "match-system-checkbox") and egu().verifycheck_checkbox("filter-options-window", "do-not-overlap-checkbox") and not egu().verifycheck_checkbox("filter-options-window", "match-installed-checkbox")):
			logging.info("It's successful to check filter_options_persisted_in_session")
		else:
			raise error.TestFail("Test Faild - Failed to check filter_options_persisted_in_session")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check filter_options_persisted_in_session:" + str(e))
	finally:
		egu().capture_image("filter_options_persisted_in_session")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
