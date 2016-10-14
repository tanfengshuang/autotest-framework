import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.compare_skus import *
from autotest_lib.client.tests.kvm.tests.skutest.sku_attribute_test import *
from autotest_lib.client.tests.kvm.tests.skutest.download_all_skus import *

def run_tc_SKU_attribute_Multiplier(test, params, env):
	session,vm = eu().init_session_vm(params,env)
	
	logging.info("========================== Begin of Running Test Case: %s ==========================="%__name__)

	try:       
		attribute = "Multiplier"
		sku_param = params.get("sku")
		
		auto_client_path = os.environ['AUTODIR']
        	reference_doc_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Reference_standard.txt")

		sku_attribute_common(session, params, attribute)
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		#os.remove(sku_regression_attributes_path)
		logging.info("========================= End of Running Test Case: %s ========================="%__name__)
