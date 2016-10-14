import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115151_register_using_firstboot_after_registering_by_cert_mode(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)
	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		egu().open_firstboot(session)
		egu().welcome_forward_click()
		egu().license_forward_click()
		if egu().check_object_exist('firstboot-main-window', 'firstboot-registeration-warning-label'):
			logging.info("It's successful to check register_using_firstboot_after_registering_by_cert_mode.")
		else:
			raise error.TestFail("Test Failed - Failed to check register_using_firstboot_after_registering_by_cert_mode.")
		egu().software_update_forward_click()
		egu().create_user_forward_click()
		egu().donot_set_user_yes_button()
		egu().date_time_forward_click()
		egu().kdump_ok_button()
		egu().kdump_finish_button()
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check register_using_firstboot_after_registering_by_cert_mode:" + str(e))
	finally:
		egu().capture_image("filter_options_persisted_in_session")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
