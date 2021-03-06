import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115177_GUI_unregister(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().register_in_gui(username, password)
		egu().check_consumer_cert_files(session, True)
		egu().click_unregister_menu()
		if egu().check_consumer_cert_files(session, False):
			logging.info("It's successful to check certificate files are dropped into /etc/pki/consumer")
		else:
			raise error.TestFail("Test Faild - Failed to check certificate files are dropped into /etc/pki/consumer")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check unregister via GUI:" + str(e))
	finally:
		egu().capture_image("check_register_succeed")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)