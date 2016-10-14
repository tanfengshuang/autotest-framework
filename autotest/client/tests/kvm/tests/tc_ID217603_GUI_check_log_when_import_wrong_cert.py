import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID217603_GUI_check_log_when_import_wrong_cert(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		
		# click register button
		egu().click_ImportCertificate_button()
		egu().click_Certificate_Location()
		egu().input_location("/tmp/doesnotexistblahblah.pem")
		egu().click_import_cert_button()
		egu().close_error_cert_dialog()
		# since 6.4 is different with 6.4, so will complete it later, check log, check dialog opened.
# 		if egu().get_my_subscriptions_table_row_count() >= 1:
# 			logging.info("It's successful to auto subscribe: %s" % egu().get_my_subscriptions_table_my_subscriptions())
# 		else:
# 			raise error.TestFail("Test Faild - Failed to register and auto subscribe via GUI!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check importing wrong cert:" + str(e))
	finally:
		egu().capture_image()
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
