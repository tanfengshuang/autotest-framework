import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262268_rct_report_contract_number(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		manifestlocal = "/root/"
		manifestserver = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/productpki/manifest_1.zip"
		eu().copyfiles(vm, manifestserver, manifestlocal, cmddesc="copying manifest to the dir: %s" %manifestlocal)
		
		#list version of subscription-manager pythonrhsm and candlepin
		cmd = "rct cat-manifest /root/manifest_1.zip | grep Contract:"
		(ret,output) = eu().runcmd(session, cmd, "check the manifest's Contract")
		contract = output.split(':')[1].strip()
		if ret == 0 and contract:
			logging.info("It's successful to check the manifest's Contract.")
		else:
			raise error.TestFail("Test Failed - Failed to check the manifest's Contract .")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the manifest's Contract:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
