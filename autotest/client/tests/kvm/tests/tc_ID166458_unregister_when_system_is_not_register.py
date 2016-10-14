import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID166458_unregister_when_system_is_not_register(test, params, env):
        session,vm=eu().init_session_vm(params,env)

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
        try:
                if eu().sub_isregistered(session):
                     	eu().sub_unregister(session)
                     	
        	cmd='subscription-manager unregister'
        	(ret,output)=eu().runcmd(session,cmd,"unregister when system is not registered",timeout=60)

        	if ret == 1 and 'This system is currently not registered' in output:
                	logging.info("Test Successful - It's successful to verify unregister command when system is not registered.")
        	else:
                	raise error.TestFail("Test Failed - Failed to verify unregister command when system is not registered.")
                	
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do unregister_when_system_is_not_register"+str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
