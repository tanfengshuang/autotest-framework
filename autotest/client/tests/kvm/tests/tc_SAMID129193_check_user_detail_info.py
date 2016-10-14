import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129193_check_user_detail_info(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#create a user
		eu().sam_create_user(session, ee.username1ss, ee.password1ss, ee.email1)

		#check user detail info
                cmd="headpin -u admin -p admin user info --username=%s" %(ee.username1ss)
		(ret,output)=eu().runcmd(session,cmd,"check user detail info")

                if (ret == 0) and (ee.username1ss in output) and (ee.email1 in output):
                        logging.info("It's successful to check user %s detail info."%(ee.username1ss))
                else:
                        raise error.TestFail("It's failed to check user %s detail info."%(ee.username1ss))
                        
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do check a user detail info:"+str(e))
	finally:
		eu().sam_delete_user(session, ee.username1ss)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

