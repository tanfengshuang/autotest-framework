import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_prod import ent_prod as ep
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_content_jboss(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)
	try:
		try:         
                        # Get and print params of python command for content test
                        eu().cnt_command_params_content(params)

	                #[A]Prepare test data	                
	                content_level = params.get("content_level")
	                baseurl = params.get("baseurl")
	                hostname = params.get("hostname")

	                if ("stage" in hostname):
		                username = "stage_test_87"
	        	        password = "redhat"
	                	sku = "MW2037717"
	                else:
		                username = ee.username_qa
	        	        password = ee.password_qa
	                        sku = "SYS0395"
	
			productid_cont = '183,185'
	
			release_list = params.get('release_list')
	
	                #[B]Run the test
			(prodsku, basesku) = ep().cnt_get_prodsku_and_basesku(sku)
			ep().cnt_rhel_test(session, vm, username, password, prodsku, basesku, productid_cont, content_level, "", release_list)
								                 
		except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when do content testing:" + str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

