import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu
def run_tc_ID115153_register_using_firstboot_by_certmode(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)
	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		egu().open_firstboot(session)
		egu().welcome_forward_click()
		egu().license_forward_click()
		egu().software_update_forward_click()
		egu().choose_service_forward_click()
		egu().registeration_with_forward_click()
		egu().input_firstboot_username(username)
		egu().input_firstboot_password(password)
		egu().check_firstboot_manual()
		egu().enter_account_info_forward_click()
		egu().skip_auto_forward_click()
		egu().create_user_forward_click()
		egu().donot_set_user_yes_button()
		egu().date_time_forward_click()
		egu().kdump_ok_button()
		egu().kdump_finish_button()
		if eu().sub_checkidcert(session):
			logging.info("It's successful to register by certmode using firstboot")
		else:
			raise error.TestFail("Failed to register by certmode using firstboot")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to register by certmode using firstboot:" + str(e))

	finally:
		egu().capture_image("register by certmode using firstboot")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
