import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID126354_import_invalid_entitlement_cert_via_CLI(test, params, env):
	
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#get username and password
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		autosubprod=ee().get_env(params)["autosubprod"]
		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)
		
		cmd='cat /etc/pki/entitlement/*.pem > /home/foo.pem'
		(ret,output)=eu().runcmd(session,cmd,"prepare a invalid pem file")
		if ret == 0:
			cmd='subscription-manager unsubscribe --all'
			(ret,output)=eu().runcmd(session,cmd,"unsubscribe")
			if ret == 0:
				cmd='subscription-manager import --certificate=/home/foo.pem'
				(ret,output)=eu().runcmd(session,cmd,"Import an entitlement cert")
				if ret == 0 and "Successfully imported certificate foo.pem" in output:
					cmd='subscription-manager list --consumed'
					(ret,output)=eu().runcmd(session,cmd,"list consumed")
					if ret ==0 and 'Consumed Subscriptions' in output:
						logging.info('It is successful to verify importing invalid entitlement cert via CLI')
					else:
						raise error.TestFail("Test Failed - Failed to list consumed subscriptions.")
				else:
					raise error.TestFail("Test Failed - Failed to importing invalid entitlement cert via CLI")
			else:
				raise error.TestFail("Test Failed - Failed to unsubscribe")
		else:
			raise error.TestFail("Test Failed - Failed to prepare a invalid pem file")  
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do verify importing invalid entitlement cert via CLI"+str(e))
        finally:
		cmd='rm -rf /home/foo.pem'
		(ret,output)=eu().runcmd(session,cmd,"remove /home/foo.pem file")
		eu().sub_unregister(session)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
