"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID178151_mess_up_identity_certificate(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		#register
		eu().sub_register(session,username,password)
	
		#edit the cert.pem
		mess_recover_cert(session, '/etc/pki/consumer/cert.pem', 'mess1')
		list_availalbe(session, 'mess1')
		mess_recover_cert(session, '/etc/pki/consumer/cert.pem', 'recover')
		list_availalbe(session, 'recover')
		
		#edit the key.pem
		mess_recover_cert(session, '/etc/pki/consumer/key.pem', 'mess2')
		list_availalbe(session, 'mess2')
		mess_recover_cert(session, '/etc/pki/consumer/key.pem', 'recover')
		list_availalbe(session, 'recover')

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when register with invalid consumerid:"+str(e))
	finally:
		eu().sub_unregister(session)
		clean_certs(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def mess_recover_cert(session, cert, direct):
	if direct=='mess1':
		cmd='sed -i "s/-----BEGIN CERTIFICATE-----/-----BEGIN CERTIFICATE-----\\nQQQQQ/g" %s'%cert
	elif direct=='mess2':
		cmd='sed -i "s/-----BEGIN RSA PRIVATE KEY-----/-----BEGIN RSA PRIVATE KEY-----\\nQQQQQ/g" %s'%cert
	elif direct=='recover':
		cmd='sed -i "/QQQQQ/d" %s'%cert
	else:
		raise error.TestFail("Test Failed - error happened to identify the command to run")

	(ret,output)=eu().runcmd(session,cmd,"edit the identity cert")
	if ret==0:
		logging.info("It's successful to %s the %s"%(direct,cert))
	else:
		raise error.TestFail("Test Failed - error happened to edit the cert")
	
def list_availalbe(session, direct):
	cmd_list="subscription-manager list --available"
	(ret,output)=eu().runcmd(session,cmd_list,"list the available subscriptions")
	if ret!=0:
		if(direct=='mess1' and ("This system is not yet registered" in output)) or (direct=='mess2' and ("bad base64 decode" in output)):
			logging.info("It's successful to verify that no subscription is available with changed identity cert!")
	elif direct=='recover' and ret==0:
			logging.info("It's successful to verify that available subscription is listed with recovered identity cert!")
	else:
		raise error.TestFail("Test Failed - error happened when list available subscriptions")
		
def clean_certs(session):
	cmd='subscription-manager clean'
	(ret,output)=eu().runcmd(session,cmd,"clean the certs so that the test case will not influence other cases")
	if ret==0 and 'All local data removed' in output:
		logging.info("It's successful to clean the certs to make sure that the test case will not influence other cases")
	else:
		raise error.TestFail("Test Failed - error happened when clean certs, please clean them manually to make sure that the test case will not influence other cases")
