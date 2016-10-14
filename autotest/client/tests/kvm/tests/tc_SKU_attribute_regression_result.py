import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.compare_skus import *

def run_tc_SKU_attribute_regression_result(test, params, env):
	session,vm = eu().init_session_vm(params,env)
	
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:         
		#Record the failed items during sku regression attributes test
		auto_client_path = os.environ['AUTODIR']
		sku_regression_attributes_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Regression_attribute_result.txt")
		sku_str = ""
		
		if not os.path.isfile(sku_regression_attributes_path):
			logging.info("Success to do the sku regression attributes test!")
		else:
			file_attribute = open(sku_regression_attributes_path, "r") 	
			sku_str = file_attribute.read()

			logging.info("**************************************************")
			logging.info("%s" %(sku_str))
			logging.info("**************************************************")

			os.remove(sku_regression_attributes_path)
			raise error.TestFail("Test Failed - Faild to do sku regression attributes test,following items failed: %s.\n" %(sku_str))
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		#os.remove(sku_regression_attributes_path)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
