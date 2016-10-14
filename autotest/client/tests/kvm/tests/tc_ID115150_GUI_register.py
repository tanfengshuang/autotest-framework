import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115150_GUI_register(test, params, env):

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
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to register via GUI:" + str(e))
	finally:
		egu().capture_image("check_register_succeed")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)