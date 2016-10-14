import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115158_register_with_account_without_any_orgs_access_via_GUI(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:

		samip = params.get("samhostip")
		username0="usertest"
		password0="123456"
		email0="usertest@redhat.com"
	
		#creat user on samserver
		remote_create_user(samip, username0, password0, email0)

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().click_register_button()
		egu().click_dialog_next_button()
		egu().input_username(username0)
		egu().input_password(password0)
		#register with account without orgs access
		if egu().click_dialog_register_for_account_without_org_access():
			logging.info("It's successful to check register with a user account without any orgs access via GUI")
		else:
			raise error.TestFail("TestFailed - Failed to check register with a user account without any orgs access via GUI")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check register with a user account without any orgs access via GUI:" + str(e))
	finally:
		egu().capture_image("check register with a user account without any orgs access via GUI")
		remote_delete_user(samip, username0)
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)

def remote_create_user(samip, username, password, email):
	#create user with username, password and email address
	cmd="headpin -u admin -p admin user create --username=%s --password=%s --email=%s"%(username, password, email)
	(ret, output)=eu().runcmd_remote(samip, "root", "redhat", cmd)
	if (ret == 0) and ("Successfully created user" in output):
		logging.info("It's successful to create user %s with password %s and email %s."%(username, password, email))
	else:
		raise error.TestFail("Test Failed - Failed to create user %s with password %s and email %s."%(username, password, email))

def remote_delete_user(samip, username):
	#delete user with username
	cmd="headpin -u admin -p admin user delete --username=%s"%(username)
	(ret, output)=eu().runcmd_remote(samip, "root", "redhat", cmd)
	if (ret == 0) and ("Successfully deleted user" in output):
		logging.info("It's successful to delete user %s."%(username))
	else:
		raise error.TestFail("Test Failed - Failed to delete user %s."%(username))

