import sys, os, subprocess, commands, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129199_check_org_detail_info(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#create an org
		orgname=ee.org1 + time.strftime('%Y%m%d%H%M%S')
		eu().sam_create_org(session, orgname)

		#check org detail info
                cmd="headpin -u admin -p admin org info --name=%s"%(orgname)
		(ret,output)=eu().runcmd(session,cmd,"check detail info of organization")

                if ret == 0 and "Description:" in output and orgname in output:
                        logging.info("It's successful to check detail info of organization %s."%orgname)
                else:
                        raise error.TestFail("Test Failed - Failed to check detail info of organization %s."%orgname)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do check detail info of organization:"+str(e))
	finally:
		eu().sam_delete_org(session, orgname)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

