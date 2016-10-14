import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID143288_dryrun_bind_with_specified_SLA(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)
	
	try:
		#[A] - prepare test env
		#get baseurl
		if "8443" in params.get("baseurl"):
			baseurl=params.get("baseurl")+"/candlepin"
		elif params.get("samhostip") == None:
			baseurl="https://"+params.get("hostname")+"/subscription"
		else:
			baseurl="https://"+params.get("samhostname")+"/sam/api"

		#get consumerid
		cmd="subscription-manager identity | grep identity"
		(ret,output)=eu().runcmd(session,cmd,"get consumerid")
                consumerid = output.split(':')[1].strip()

		service_level = ee().get_env(params)["servicelevel"]
		
		#[B] - run the test		
		#call dry run bind to products by api
                cmd="curl -k --cert /etc/pki/consumer/cert.pem --key /etc/pki/consumer/key.pem %s/consumers/%s/entitlements/dry-run?service_level=%s && echo \"\r\"" %(baseurl, consumerid, service_level)
                (ret,output)=eu().runcmd(session,cmd,"dry run bind by products api")
                
                if ret == 0 and ('"value":"%s"'%service_level in output or '"value":"%s"'%(((service_level).lower()).capitalize()) in output):
			logging.info("It's successful to dry run bind by products api with a specified SLA.")
                else:
                        raise error.TestFail("Test Failed - Failed to dry run bind by products api with a specified SLA.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do dry run bind by products api with a specified SLA:"+str(e))

	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


