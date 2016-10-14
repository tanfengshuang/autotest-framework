import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID154592_set_release_version(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:   
		#get env variables
		productid=ee().get_env(params)["productid"]
		autosubprod=ee().get_env(params)["autosubprod"]

		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)

		#set releases
		guestname=params.get("guest_name")
		currentversion=eu().sub_getcurrentversion(session,guestname)
		cmd="subscription-manager release --set=%s"%(currentversion)
		(ret,output)=eu().runcmd(session,cmd,"set release version")
		

	        if ret == 0 and "Release set to: %s"%(currentversion) in output:      
           		logging.info("It's successful to set release version.")	
                else:
        	        raise error.TestFail("Test Failed - Failed to set release version.")

		#check the version in repo list
		cmd = "subscription-manager repos --list|grep 'Repo Url'"
		cmd510 = "subscription-manager repos --list|grep 'Repo URL'"
		(ret,output)=eu().runcmd(session,cmd,"list available repos")

		if ret == 0 and currentversion in output:      
			logging.info("It's successful to display the set release version.")
		else:
			(ret,output)=eu().runcmd(session,cmd510,"list available repos")
			if ret == 0 and currentversion in output:
				logging.info("It's successful to display the set release version.")
			else:
				raise error.TestFail("Test Failed - Failed to display the set release version.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when set release version:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
