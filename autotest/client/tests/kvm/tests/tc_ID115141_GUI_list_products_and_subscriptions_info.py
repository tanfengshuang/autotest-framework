import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115141_GUI_list_products_and_subscriptions_info(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_and_autosubscribe_in_gui(username, password)
		productid = ee().get_env(params)["productid"]
		egu().click_my_installed_products_tab()
		for item in eu().sub_listinstalledpools(session):
			if not egu().check_content_in_my_installed_products_table(item["SubscriptionName"]):
				raise error.TestFail("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
		egu().click_my_subscriptions_tab()
		# check sub_listavailpools are all shown in gui
		for item in eu().sub_listconsumedpools(session):
			if not egu().check_content_in_my_subscriptions_table(item["SubscriptionName"]):
				raise error.TestFail("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
		# detail info not added yet
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check list_products_and_subscriptions_info:" + str(e))
	finally:
		egu().capture_image("check_list_products_and_subscriptions_info")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
