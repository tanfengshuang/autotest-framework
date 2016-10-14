import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID189605_GUI_service_level_should_shown_correctly(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_and_autosubscribe_in_gui(username, password)
		servicelevel = ee().get_env(params)["servicelevel"]
		cmd = "subscription-manager service-level --set=%s" % servicelevel
		(ret, output) = eu().runcmd(session, cmd, "set service level as %s" % servicelevel)
		if ret == 0 and "Service level set to: %s" % servicelevel in output:
			logging.info("It's successful to set service level %s." % servicelevel)
		else:
			raise error.TestFail("Test Failed - Failed to set service level %s." % servicelevel)
		egu().click_preferences_menu()
		if egu().check_object_exist("system-preferences-dialog", "service-level-" + servicelevel.lower() + "-combobox"):
			logging.info("It's successful to check service_level_should_shown_correctly.")
		else:
			raise error.TestFail("Test Faild - Failed to check service_level_should_shown_correctly!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check service_level_should_shown_correctly:" + str(e))
	finally:
		egu().capture_image("service_level_should_shown_correctly")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
