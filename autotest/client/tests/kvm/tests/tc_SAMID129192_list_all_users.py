import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129192_list_all_users(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#create a user
		eu().sam_create_user(session, ee.username1ss, ee.password1ss, ee.email1)

		#list user
                cmd="headpin -u admin -p admin user list"
		(ret,output)=eu().runcmd(session,cmd,"list user")

                if (ret == 0) and (ee.username1ss in output):
                        logging.info("It's successful to list user %s."%(ee.username1ss))
                else:
                        raise error.TestFail("It's failed to list user %s."%(ee.username1ss))
                        
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list a user:"+str(e))
	finally:
		eu().sam_delete_user(session, ee.username1ss)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

