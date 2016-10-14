import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.ent_gui_utils import ent_gui_utils as egu

def run_tc_ID178197_register_to_SAM_when_already_registered_using_RHN_Classic(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)
	username0="qa@redhat.com"
	password0="29W11uh4tdq7783"
	try:
		egu().register_rhn_classic(session, username0, password0)
		egu().open_subscription_manager(session)
		egu().check_window_exist('sm-gui-warning-classic-dialog')
		if egu().check_object_exist('sm-gui-warning-classic-dialog', 'warning-classic-already-label'):
			logging.info("It's successful to check register to SAM when already registered using RHN Classic via GUI.")
		else:
			raise error.TestFail("Test Failed - Failed to register to SAM when already registered using RHN Classic.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to register to SAM when already registered using RHN Classic:" + str(e))

	finally:
		egu().capture_image("register to SAM when already registered using RHN Classic")
		egu().unregister_rhn_classic(session)
		egu().restore_gui_environment(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)
