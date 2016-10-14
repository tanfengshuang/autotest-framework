import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID143277_GUI_autosubscribe_twice(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_in_gui(username, password)
		egu().click_autoattach_button()
		egu().click_attach_button()
		egu().click_my_subscriptions_tab()
		if egu().get_my_subscriptions_table_row_count() >= 1:
			logging.info("It's successful to auto subscribe: %s" % egu().get_my_subscriptions_table_my_subscriptions())
		else:
			raise error.TestFail("Test Faild - Failed to auto subscribe via GUI!")
		check_entitlement_cert_files(session)
		egu().click_remove_subscriptions_button()
		check_entitlement_cert_files(session, False)
		# repeat
		egu().click_my_installed_products_tab()
		egu().click_autoattach_button()
		egu().click_attach_button()
		egu().click_my_subscriptions_tab()
		if egu().get_my_subscriptions_table_row_count() >= 1:
			logging.info("It's successful to auto subscribe: %s" % egu().get_my_subscriptions_table_my_subscriptions())
		else:
			raise error.TestFail("Test Faild - Failed to register and auto subscribe via GUI!")
		check_entitlement_cert_files(session)
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe twice:" + str(e))
	finally:
		egu().capture_image("check_autosubscribe_twice")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)

def check_entitlement_cert_files(session, exist=True):
	cmd = "ls /etc/pki/entitlement"
	(ret, output) = eu().runcmd(session, cmd, "check certificate files in /etc/pki/entitlement")
	if exist:
		if ret == 0 and "pem" in output and "key.pem" in output:
			logging.info("It is successful to check certificate files in /etc/pki/entitlement")
		else:
			raise error.TestFail("Failed to check certificate files in /etc/pki/entitlement")
	else:
		if not (ret == 0 and "pem" in output and "key.pem" in output):
			logging.info("It is successful to check certificate files in /etc/pki/entitlement")
		else:
			raise error.TestFail("Failed to check certificate files in /etc/pki/entitlement")
