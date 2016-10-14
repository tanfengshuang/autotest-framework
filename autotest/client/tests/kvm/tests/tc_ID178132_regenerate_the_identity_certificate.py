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

def run_tc_ID178132_regenerate_the_identity_certificate(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]

		#register to candlepin
		eu().sub_register(session,username,password)
	
		# check identity and record the identity information
		cmd_check="subscription-manager identity"
		(ret,output)=eu().runcmd(session,cmd_check,"run subscription-manager identity")
		identity_info1=output
		if ret==0:
			logging.info("It's successful to display identity 1 info!")
		else:
			raise error.TestFail("Test Failed - Failed to display identity 1 info")

		# check cert information
		cmd_check_cert="stat /etc/pki/consumer/cert.pem | grep -i Modify | awk -F. '{print $1}' | awk '{print $2$3}'| awk -F- '{print $1$2$3}' | awk -F: '{print $1$2$3}'"
		(ret,output)=eu().runcmd(session,cmd_check_cert,"check consumer certs")
		if ret==0:
			modified_date1=output
			logging.info("It's successful to gain the certs information and record the modified time for first time!")
		else:
			raise error.TestFail("Test Failed - Failed to display modified info")

		#regenerate the certs
		cmd_regenerate="subscription-manager identity --regenerate --username=%s --password='%s' --force"%(username,password)
		(ret,output)=eu().runcmd(session,cmd_regenerate,"regenerate the identity certs")
		if ret==0 and "Identity certificate has been regenerated" in output:
			logging.info("It's successful to regenerate the identity certs")
		else:
			raise error.TestFail("Test Failed - Failed to regenerate the identity certs")
	
		#check identity and record the identity information
		cmd_check="subscription-manager identity"
		(ret,output)=eu().runcmd(session,cmd_check,"run subscription-manager identity")	 
		identity_info2=output
		if ret==0:
			logging.info("It's successful to display identity 2 info!")
		else:
			raise error.TestFail("Test Failed - Failed to display identity 2 info")

		# check wether the identity infos are the same
		if identity_info1==identity_info2:
			logging.info("It's successful to verify that the identity infos are the same")
		else:
			raise error.TestFail("Test Failed - Failed to verify that the identity infos are the same")

		# check cert information
		cmd_check_cert="stat /etc/pki/consumer/cert.pem | grep -i Modify | awk -F. '{print $1}' | awk '{print $2$3}'| awk -F- '{print $1$2$3}' | awk -F: '{print $1$2$3}'"
		(ret,output)=eu().runcmd(session,cmd_check_cert,"check consumer certs") 
		if ret==0:
			modified_date2=output
			logging.info("It's successful to gain the certs information and record the modified time for second time!")
		else:
			raise error.TestFail("Test Failed - Failed to display modified info")
	
		# check wether the certs are renewed
		if int(modified_date2) > int(modified_date1):
			logging.info("It's successful to verify that the certs have been renewed")
		else:
			raise error.TestFail("Test Failed - Failed to verify that the certs have been renewed")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when verify registering with invalid username and password:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

