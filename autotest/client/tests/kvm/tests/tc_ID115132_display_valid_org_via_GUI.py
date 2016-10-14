import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115132_display_valid_org_via_GUI(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		samip = params.get("samhostip")
		
		#creat org on samserver
		remote_create_org(samip)

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().click_register_button()
		egu().click_dialog_next_button()
		egu().input_username(username)
		egu().input_password(password)
		egu().click_dialog_register_button()
		
		if egu().check_table_value_exist('register-dialog', 'orgs-view-table', 'qianqian') and egu().check_table_value_exist('register-dialog', 'orgs-view-table', 'ACME_Corporation'):
			logging.info("It's successful to display the valid orgs list.")
		else:
			raise error.TestFail("Test Faild - Failed to display the valid orgs list")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to display the valid orgs list:" + str(e))
	finally:
		egu().capture_image("display the valid orgs list")
		remote_delete_org(samip)
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)

def remote_create_org(samip):
	cmd_create="headpin -u admin -p admin org create --name=qianqian"
	(ret, output) = eu().runcmd_remote(samip, "root", "redhat", cmd_create)
	if ret==0 and "Successfully created org" in output:
		logging.info("It's successful to create a new org in SAM server")
	else:
		raise error.TestFail("TestFailed - Failed to create a new org!")
		
def remote_delete_org(samip):
	cmd_delete="headpin -u admin -p admin org delete --name=qianqian"
	(ret, output) = eu().runcmd_remote(samip, "root", "redhat", cmd_delete)
	if ret==0 and "Successfully deleted org" in output:
		logging.info("It's successful to delete the new org in SAM server")
	else:
		raise error.TestFail("TestFailed - Failed to delete a new org!")
