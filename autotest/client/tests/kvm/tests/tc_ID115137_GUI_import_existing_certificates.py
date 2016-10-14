import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115137_GUI_import_existing_certificates(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		# register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		# auto-subscribe a subscription
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		generate_cert(session)
		eu().sub_unregister(session)
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		# click register button
		egu().click_register_button()
		egu().click_dialog_next_button()
		egu().input_username(username)
		egu().input_password(password)
		egu().click_dialog_register_button()
		egu().click_dialog_cancle_button()
		egu().click_import_cert_menu()
		egu().click_Certificate_Location()
		egu().click_type_file_name_button()
		egu().input_location("/tmp/test.pem")
		egu().click_open_file_button()
		if egu().check_window_open("information-dialog") and egu().check_object_exist("information-dialog", "import-cert-success-label"):
			logging.info("It's successful to check prompt message displayed ")
		else:
			raise error.TestFail("Test Faild - Failed to check prompt message displayed")
		# check whether entitlement certificates generated and productid in them or not
		productid = ee().get_env(params)["productid"]
		eu().sub_checkentitlementcerts(session, productid)
		egu().click_my_subscriptions_tab()
		if eu().get_my_subscriptions_table_my_subscriptions() == productid:
			logging.info("It's successful to check subscriptions under my_subscriptions tab")
		else:
			raise error.TestFail("Test Faild - Failed to check subscriptions under my_subscriptions tab")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check import existing certificates:" + str(e))
	finally:
		egu().capture_image("check_subscription_after_import_cert")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)

def generate_cert(session):
	cmd = "cat /etc/pki/entitlement/* > /tmp/test.pem"
	(ret, output) = eu().runcmd(session, cmd, "generate entitlement cert")
	if ret == 0:
		logging.info("It's successful to generate entitlement cert")
	else :
		raise error.TestFail("Test Failed - error happened when generate entitlement certs")
