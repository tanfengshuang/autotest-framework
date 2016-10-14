import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115198_listavailrepos(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		#[A] - prepare test env
		#get env variables
		productid=ee().get_env(params)["productid"]
		autosubprod=ee().get_env(params)["autosubprod"]

		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)

		#check whether entitlement certificates generated and productid in them or not
		#eu().sub_checkentitlementcerts(session,productid)      

		#[B] - run the test
		#list available repos
                cmd="subscription-manager repos --list"
		(ret,output)=eu().runcmd(session,cmd,"list available repos")
                
		productrepo=ee().get_env(params)["productrepo"]
		betarepo=ee().get_env(params)["betarepo"]
                if ret == 0 and productrepo in output and betarepo in output:
			logging.info("It's successful to list available repos.")
                else:
                        raise error.TestFail("Test Failed - Failed to list available repos.")
                
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list available repos:"+str(e))
	finally:
                eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


