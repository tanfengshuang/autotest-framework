import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID143275_auto_subscribe_with_single_SLA_GUI(test,params,env):
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)
	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		
		eu().sub_register(session, username, password)
		egu().open_subscription_manager(session)
		egu().click_autoattach_button()
		egu().click_attach_button()
		subscription=egu().get_table_cell('main-window', 'my-subscription-table', 0, 0)
		if subscription == 'Red Hat Employee Subscription' or subscription == 'Red Hat Enterprise Linux Server, Premium (8 sockets) (Up to 4 guests)':
			logging.info("It's successful to auto_subscribe_with_single_SLA_GUI")
		else:
			raise error.TestFail("Test Faild - Failed to auto_subscribe_with_single_SLA_GUI")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("error happened to auto_subscribe_with_single_SLA_GUI:"+str(e))
	finally:
		egu().capture_image("auto_subscribe_with_single_SLA_GUI")
		egu().restore_gui_environment(session)
		logging.info("===============End of Running Test Case: %s"%__name__)
                
