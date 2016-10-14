import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils,virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190639_register_selected_server(test,params,env):
		
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	
	try:
		
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		baseurl=params.get("baseurl")

		candlepinhostname=params.get("candlepinhostname")
		candlepinhostip=params.get("candlepinhostip")

		samhostname=params.get("samhostname")
		samhostip=params.get("samhostip")

		#register to local candlepin server
		if candlepinhostname != None and candlepinhostip != None and baseurl == 'https://%s:8443'%candlepinhostname:
			serverurl='https://'+candlepinhostname+':8443'+'/candlepin'
			cmd="subscription-manager register --username=%s --password=%s --serverurl=%s"%(username,password,serverurl)		

		#register to sam candlepin server
		elif samhostname != None and samhostip != None and baseurl == 'https://%s:8088'%samhostname:
			serverurl='https://'+samhostname+':443'+'/sam/api'
			cmd="subscription-manager register --username=%s --password=%s --serverurl=%s --org=ACME_Corporation"%(username,password,serverurl)	
		
		#register to stage/product candlepin server
		else:
			hostname=params.get('hostname')
			serverurl='https://'+hostname+':443'+'/subscription'
			cmd="subscription-manager register --username=%s --password=%s --serverurl=%s"%(username,password,serverurl)	
	
		(ret,output)=eu().runcmd(session,cmd,"register to selected server")
		if ret == 0 and ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
			logging.info("It is successful to register system to selected server.")
		else:
			raise error.TestFail("Test Failed - Failed to rigster system to selected server.")
					
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to rigster system to selected server:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

