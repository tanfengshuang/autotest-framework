import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.compare_skus import *

def run_tc_SKU_consistency_verify_mapping_reference(test, params, env):
	session,vm = eu().init_session_vm(params,env)
	
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:         
		#compare the sku consistency between the sku regression attributes code and reference doc-95917
		auto_client_path = os.environ['AUTODIR']
		desc_path = os.path.join(auto_client_path.replace("autotest/client",""),"desc")
		sku_regression_attributes_desc = os.path.join(desc_path, "entitlement_sku_regression_mapping_test.desc") 
		
		reference_doc_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Reference_standard.txt")

		skus_consistency_test(sku_regression_attributes_desc, reference_doc_path)
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
