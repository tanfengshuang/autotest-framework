import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190594_run_identity_when_regitered(test, params, env):

        session,vm=eu().init_session_vm(params,env)
        logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
		#register the system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

                cmd='subscription-manager identity'
                (ret,output)=eu().runcmd(session,cmd,"running identity command")
                if ret == 0 and (('system identity' in output) and ('name' in output) and ('org name' in output) \
                  and ('org id' in output or 'org ID' in output)):
                        logging.info("It's successful to check the output of identity command when the machine is registered.") 
                else:
                        raise error.TestFail("Test Failed - Failed to check the output of identity command when the machine is registered.")
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened to check the output of identity command when the machin is registered:"+str(e))
        finally:
		eu().sub_unregister(session)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
