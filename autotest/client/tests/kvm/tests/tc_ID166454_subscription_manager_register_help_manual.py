import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID166454_subscription_manager_register_help_manual(test, params, env):
        session,vm=eu().init_session_vm(params,env)

        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
        try:
                cmd='subscription-manager --help'
                (ret,output)=eu().runcmd(session,cmd,"list subscription-manager help manual!")
                if ret == 0 and ('Primary Modules' and 'Other Modules' in output):
                        logging.info("Test Successful - It's successful to list subscription-manager help manual.") 
                else:
                        raise error.TestFail("Test Failed - Failed to list subscription-manager help manual.")
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do list subscription-manager help"+str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
