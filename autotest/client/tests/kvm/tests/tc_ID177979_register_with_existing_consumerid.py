"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID177979_register_with_existing_consumerid(test, params, env):
	session,vm=eu().init_session_vm(params,env)
	logging.info("==================Begin of Running Test Case: %s============="%__name__)
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		consumer_certpath = '/etc/pki/consumer'
		entitlement_certpath ='/etc/pki/entitlement'
		#register firstly
		eu().sub_register(session,username,password)
		#record consumerid
		consumerid=eu().sub_get_consumerid(session)
		#autosubscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		#check certs the first time
		consumer1_cert_md5=md5_value(session,consumer_certpath)
		entitlement1_cert_md5=md5_value(session,entitlement_certpath)

		#clean the client data
		cmd="subscription-manager clean"
		(ret,output)=eu().runcmd(session,cmd,"run subscription-manager clean")
		if (ret==0) and ("All local data removed" in output):
			logging.info("It's successful to run subscription-manager clean")
		else:
			raise error.TestFail("Test Failed - error happened when run subscription-manager clean")
		#register with consumerid
		cmd="subscription-manager register --username=%s --password=%s --consumerid=%s"%(username, password, consumerid)
		(ret,output)=eu().runcmd(session,cmd,"register with existing consumerid")
		if (ret==0) and ("The system has been registered with ID:" in output):
			logging.info("It's successful to register with existing consumerid")
		else:
			raise error.TestFail("Test Failed - error happened when register with existing consumerid")

		#check certs the second time
		consumer2_cert_md5=md5_value(session,consumer_certpath)
		entitlement2_cert_md5=md5_value(session,entitlement_certpath)
		#compare certs md5sum
		if consumer1_cert_md5==consumer2_cert_md5 and entitlement1_cert_md5==entitlement2_cert_md5:
			logging.info("It's successful to check the consumer certs and entitlement certs")
		else:
			raise error.TestFail("Test Failed - Failed to check the consumer certs and entitlement certs")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check whether certs come back correctly:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def md5_value(session,certpath):
	cmd="md5sum `ls %s/*.pem`"%(certpath)
	(ret,output)=eu().runcmd(session,cmd,"get md5sum value of cert files in %s " % certpath)
	if ret==0 and output!=None:
		logging.info("It's successful to get md5sum value of cert files in %s " % certpath)
		return output
	else:
		raise error.TestFail("Test Failed - Failed to get md5sum value of cert files in %s " % certpath)
