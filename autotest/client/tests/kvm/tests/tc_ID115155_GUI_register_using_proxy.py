import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID115155_GUI_register_using_proxy(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]

		# open subscription-manager-gui
		egu().open_subscription_manager(session)
		egu().check_consumer_cert_files(session, False)
		# click register button
		egu().click_register_button()
		egu().click_configure_proxy_button()
		egu().check_HTTP_proxy_checkbox()
		egu().input_HTTP_proxy("squid.corp.redhat.com:3128")
		egu().click_proxy_close_button()
		egu().click_dialog_next_button()
		egu().input_username(username)
		egu().input_password(password)
		egu().check_manual_attach_checkbox()
		egu().click_dialog_register_button_without_autoattach()
		if egu().check_consumer_cert_files(session):
			logging.info("It's successful to check certificate files are dropped into /etc/pki/consumer")
		else:
			raise error.TestFail("Test Faild - Failed to check certificate files are dropped into /etc/pki/consumer")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to register using proxy via GUI:" + str(e))
	finally:
		remove_proxy(session)
		egu().capture_image("check_register_succeed")
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
def remove_proxy(session):
	cmd="sed -i -e 's/proxy_hostname =.*/proxy_hostname =/g' -e 's/proxy_port =.*/proxy_port =/g' /etc/rhsm/rhsm.conf"
	(ret, output)=eu().runcmd(session, cmd, "remove proxy")
	if ret == 0:
		logging.info("It's successful to remove proxy.")
	else:
		error.TestFail("Test Failed - Failed to Remove proxy")
