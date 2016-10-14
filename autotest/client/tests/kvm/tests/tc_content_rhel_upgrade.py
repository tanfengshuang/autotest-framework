import sys, os, subprocess, commands, random, re
import logging
import time
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_prod import ent_prod as ep
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_content_rhel_upgrade(test, params, env):
        session, vm = eu().init_session_vm(params, env)
        logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

        try:
                try:
                        # Get and print params of python command for content test
                        eu().cnt_command_params_content(params)

			# part1 - register and subscribe
			## get username and password
                        hostname = params.get("hostname")
                        baseurl = params.get("baseurl")
                        if ("stage" in hostname):
                                username = ee().get_env(params)["username"]
                                password = ee().get_env(params)["password"]
                                sku = ee().get_env(params)["productid"]
                        else:
                                username = ee.username_qa
                                password = ee.password_qa
                                sku = "SYS0395"

			## Rigster to server
	                eu().sub_register(session,username,password)
	
	                ## auto subscribe to a pool
	                autosubprod = ee().get_env(params)["autosubprod"]
	                eu().sub_autosubscribe(session,autosubprod)

			## yum clean and repolist
			eu().cnt_yum_clean_cache(session)	
			eu().cnt_yum_repolist(session)
			
			## yum update
			cmd = 'yum update -y'
                        (ret,output) = eu().runcmd(session,cmd,"yum update",timeout=200000)
                        if ret == 0:
                                logging.info('It is successfully to yum update')
                        else:
                                logging.error('It is failed to update')
		
			# part2 - reboot code
			cmd = 'reboot'
			(ret,output) = eu().runcmd(session,cmd,"reboot")
	                if ret == 0:
	                        logging.info('It is successfully to reboot')
	                else:
	                        logging.error('It is failed to reboot')
	
			# part3 - sleep code
	                logging.info('Sleep 300s now....')
			time.sleep(300)
	
			# part4 - get new session
			logging.info('End of sleep!')
			session,vm=eu().init_session_vm(params,env)
	
			# part5 - your code
	                cmd = 'touch \'/tmp/file22\''
	                (ret,output)=eu().runcmd(session,cmd,"create a test file /tmp/file22")
	                if ret == 0:
	                        logging.info('It is successfully to create file22')
	
	                else:
	                        logging.error('It is failed to create file22')


                except Exception, e:
                        logging.error(str(e))
                        raise error.TestFail("Test Failed - error happened when do rhel upgrade testing:"+str(e))
        finally:
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)


