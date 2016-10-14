import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115139_GUI_list_available_pools(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_in_gui(username, password)
		egu().click_all_available_subscriptions_tab()
		egu().click_update_button()
		# check sub_listavailpools are all shown in gui
		productid = ee().get_env(params)["productid"]
		for item in eu().sub_listavailpools(session, productid):
			print item
			if not egu().check_content_in_all_subscription_table(item["SubscriptionName"]):
				raise error.TestFail("Test Faild - Failed to list %s in all-subscription-table" % item["SubscriptionName"])
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check available pools:" + str(e))
	finally:
		egu().capture_image("check_available_pools")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
