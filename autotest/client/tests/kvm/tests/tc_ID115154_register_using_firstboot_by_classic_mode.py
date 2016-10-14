import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115154_register_using_firstboot_by_classic_mode(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)
	try:
		username = "qa@redhat.com"
		password = "29W11uh4tdq7783"
		#load firstboot
		egu().open_firstboot(session)
		#click welcome-forward button
		egu().welcome_forward_click()
		#click license-forward button
		egu().license_forward_click()
		#click software_update_forward button
		egu().software_update_forward_click()
		#select classic mode in firstboot
		egu().select_classic_mode()
		#click choose service forward button
		egu().choose_service_forward_click()
		#input login and password
		egu().input_firstboot_classic_username(username)
		egu().input_firstboot_classic_password(password)
		#click redhat account forward button
		egu().firstboot_classic_redhat_account_forward_button_click()
		#click OS-releaseversion-forward button
		egu().firstboot_classic_os_release_forward_button_click()
		#input system name
		egu().firstboot_classic_input_systemname()
		#click profile create forward button
		egu().firstboot_classic_profile_forward_button_click()
		#click review subscription forward button
		egu().firstboot_classic_reviewsubscription_forward_button_click()
		#click finish update button
		egu().firstboot_classic_finishupdate_forward_button_click()
		egu().create_user_forward_click()
		egu().donot_set_user_yes_button()
		egu().date_time_forward_click()
		egu().kdump_ok_button()
		egu().kdump_finish_button()
		if not egu().check_object_exist("firstboot-main-window", "firstboot-main-window"):
			logging.info("It's successful to register using firstboot by classic mode")
		else:
			raise error.TestFail("Test Failed - error happened to register using firstboot by classic mode")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to register using firstboot by classic mode:" + str(e))
	finally:
		egu().capture_image("register using firstboot by classic mode")
		egu().unregister_rhn_classic(session)
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
