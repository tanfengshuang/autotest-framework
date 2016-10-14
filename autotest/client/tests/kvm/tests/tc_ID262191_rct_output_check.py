import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262191_rct_output_check(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		manifestlocal = "/root/"
		manifestserver = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/productpki/manifest_1.zip"
		eu().copyfiles(vm, manifestserver, manifestlocal, cmddesc="copying manifest to the dir: %s" %manifestlocal)

		cmd = "rct cat-manifest /root/manifest_1.zip | grep Subscription: -A14"
		(ret,output) = eu().runcmd(session, cmd, "check the out put of rhsmcertd help")
		if ret == 0 and "Order:" in output and "SKU:" in output and "Service Level:" in output:
			logging.info("It's successful to verify rct cat-manifest new output.")
		else:
			raise error.TestFail("Test Failed - Failed to verify rct cat-manifest new output.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check rct cat-manifest new output:"+str(e))
	finally:
		cmd = "rm -f /root/manifest_1.zip"
		(ret, output) = eu().runcmd(session, cmd, "rm the manifest")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
