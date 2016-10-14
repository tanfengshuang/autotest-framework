import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.skutest import *
from autotest_lib.client.tests.kvm.tests.skutest.download_all_skus import *

def run_tc_SKU_mapping(test, params, env):
	session,vm=eu().init_session_vm(params,env)
	
	logging.info("========================== Begin of Running Test Case: %s ========================="%__name__)
	#sku='MCT2741'

	try:         
                # sku mapping testing
		sku_param = params.get("sku")
		if sku_param == None or sku_param == "all":
			sku_list = get_sku_list_from_reference()
		else:
			sku_list = sku_param.split(',')	
        
		#Begin to do sku mapping test for the sku_list.
		test_result = True
		#Record the failed skus in order to check the result convinently.
		failed_pool_sku_list = []
		failed_eng_sku_list = []
		for sku in sku_list:
			#check if one sku is RHUI type or not
			sku_type = check_sku_RHUI_type(sku)
			if sku_type == "RHUI": 
				result = sku_test_common(session, params, sku, sku_type)
			else:
				result = sku_test_common(session, params, sku)

			test_result &= result[0]
			if not test_result:
				if not result[1]:
					failed_pool_sku_list.append(sku)
				else:
					failed_eng_sku_list.append(sku)

		if test_result:
			logging.info("It's successful to do the sku mapping test!")
		else:
			logging.info("Due to no available pools for the subscription -- Failed to do sku mapping test for the following %s skus %s." % (len(failed_pool_sku_list), failed_pool_sku_list))
			logging.info("Due to Eng Productid(s) not match -- Failed to do sku mapping test for the following %s skus %s." % (len(failed_eng_sku_list),failed_eng_sku_list))
			raise error.TestFail("Failed to do the sku mapping test!")			
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing: "+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

