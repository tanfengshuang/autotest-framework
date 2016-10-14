#!/usr/bin/python

import os
import sys
import json
import shutil
import logging
from optparse import OptionParser
import codecs
import time
from download_all_skus import *
from get_test_values import *

########### target test values ###################
#id 
#multiplier 
#attributes:product_family 
#attributes:sockets 
#attributes:description 
#attributes:option_code 
#attributes:support_type
#attributes:arch
#attributes:type
#attributes:name
#attributes:virt_limit
#attributes:support_level
#attributes:variant
#attributes:vcpus
#attributes:required_type
#attributes:management_enabled
#attributes:support_level
#attributes:enabled_consumer_type
#attributes:virt-only
################################

def get_test_values_for_all_skus(session, params, target_read_sku_dir):
	sku_param = params.get("sku")
	sku_list = get_sku_pass_list_from_file()

	test_values = []
	for sku in sku_list:
		logging.info("++++++++++++++++++Begin to get %s attribute value.++++++++++++++++++" % sku)
		mdict = get_test_values(sku, target_read_sku_dir)
		test_values.append(mdict)
		logging.info("++++++++++++++++++End to get %s attribute value.++++++++++++++++++" % sku)
		logging.info(" ")
	
	#Save the download attributes value into a file
	auto_client_path = os.environ['AUTODIR']
        download_value_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Download_Atrritbues_Value.txt")
	#download_value_path = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/skutest/Download_Atrritbues_Value.txt"
	logging.info("Save the attribute values into file '%s'." % download_value_path) 
	f = file(download_value_path, 'w')
	str = "%s" % test_values
	f.write(str)
	f.close

if __name__ == "__main__":
	get_test_values_for_all_skus('/tmp/sku_download')
