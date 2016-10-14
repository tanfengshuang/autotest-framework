import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID125800_deploysamserver(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
                #[A]Prepare test data
                kvm_test_dir = os.path.join(os.environ['AUTODIR'],'tests/kvm/tests')
                sam_script_path=os.path.join(kvm_test_dir,'samtest')
                eu().copyfiles(vm,sam_script_path,"/tmp",cmddesc="copying samtest scripts dir")

                #[B]Run the test
                shpath="/tmp/samtest"
		manifest="/tmp/samtest/%s"%ee.default_manifest
		sambaseurl=params.get("sambaseurl")
		cmd="bash %s/samdeploy.sh %s %s" %(shpath, sambaseurl, manifest)
		(ret,output)=eu().runcmd(session,cmd,"sam deployment",timeout=200000)

        	if ret ==0 and ("Open port 443, 8443 and 8088 FAIL" not in output) and \
			("repos are not configured successfully" not in output) and \
			("Install katello-headpin-all FAIL" not in output) and \
			("katello configuration FAIL" not in output) and \
			("Creating environment FAIL" not in output) and \
			("Importing manifest FAIL" not in output):
			logging.info("It's successful to do sam deployment.")
        	else:
			raise error.TestFail("Test Failed - Faild to do sam deployment.")
					                 
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sam deployment:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

