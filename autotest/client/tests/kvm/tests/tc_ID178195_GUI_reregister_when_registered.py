import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID178195_GUI_reregister_when_registered(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().check_consumer_cert_files(session, False)
		# click register button
		egu().click_register_button()
		egu().click_dialog_next_button()
		egu().input_username(username)
		egu().input_password(password)
		egu().check_manual_attach_checkbox()
		egu().click_dialog_register_button_without_autoattach()
		if egu().check_consumer_cert_files(session):
			logging.info("It's successful to check certificate files are dropped into /etc/pki/consumer")
		else:
			raise error.TestFail("Test Faild - Failed to check certificate files are dropped into /etc/pki/consumer")
		if egu().check_object_status("main-window", "register-menu", "VISIBLE") == 0:
			logging.info("It's successful to check register-menu is not visible")
		else:
			raise error.TestFail("Test Faild - Failed to check register-menu is not visible")
		if egu().check_object_status("main-window", "unregister-menu", "VISIBLE") == 1:
			logging.info("It's successful to check unregister-menu is visible")
		else:
			raise error.TestFail("Test Faild - Failed to check unregister-menu is visible")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to reregister_when_registered:" + str(e))
	finally:
		egu().capture_image("check_reregister_when_registered")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)