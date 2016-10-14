#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, time, random, re

from autotest_lib.client.tests.kvm.tests.skutest.download_all_skus import *
from autotest_lib.client.tests.kvm.tests.skutest.get_test_values_for_all_skus import *
from autotest_lib.client.common_lib import error
import logging

def get_attribute_value_from_reference(sku, attribute, reference_path):
	refer_dict_lists = []
	refer_dict_lists = eval(open(reference_path).read())
	for dict in refer_dict_lists:
		if dict['SKU'] == sku:
			value = dict[attribute]
			logging.info("Get attribute '%s' value from Reference Doc -- '%s'." %(attribute, value))
			return value

def get_attribute_value_from_download_data(sku, attribute, reference_path):
	download_dict_lists = []
	auto_client_path = os.environ['AUTODIR']
        download_value_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Download_Atrritbues_Value.txt")
	#download_value_path = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/skutest/Download_Atrritbues_Value.txt"
        download_dict_lists = eval(open(download_value_path).read())

	matched_attribute_name = get_matched_attribute_name_between_reference_download(sku, attribute, reference_path)
        for dict in download_dict_lists:
                if dict['id'] == sku:
                        if dict.has_key(matched_attribute_name):
                                value = dict[matched_attribute_name]
                        else:
                                value = 'n/a'
                        logging.info("Get attribute '%s' value from Stage Candlepin -- '%s'." %(attribute, value))
                        return value

def get_matched_attribute_name_between_reference_download(sku, attribute, reference_path):
	sku_type = get_sku_type(sku, reference_path)
	if sku_type == "978418_type":
                attribute_dict = {'SKU':'id','Product Hierarchy: Product Category':'ph_category','Product Hierarchy: Product Line':'ph_product_line','Product Hierarchy: Product Name':'ph_product_name','Product Name':'name','Product Family':'product_family','Virt Limit':'virt_limit','Variant':'variant','Socket(s)':'sockets','Support Type':'support_type','Multiplier':'multiplier','Unlimited Product':'unlimited_product','Cores':'cores','JON Management':'jon_management','VCPU':'vcpu','Virt-only':'virt_only','Management Enabled':'management_enabled','Enabled Consumer Types':'enabled_consumer_types','Support Level':'support_level','Required Consumer Type':'requires_consumer_type','Arch':'arch','RAM':'ram'}
        else:
                if sku_type == "2013_model_type":
                        attribute_dict = {'SKU':'id','Product Hierarchy: Product Category':'ph_category','Product Hierarchy: Product Line':'ph_product_line','Product Hierarchy: Product Name':'ph_product_name','Product Name':'name','Product Family':'product_family','Virt Limit':'virt_limit','Variant':'variant','Socket(s)':'sockets','Support Type':'support_type','Multiplier':'multiplier','Unlimited Product':'unlimited_product','Cores':'cores','JON Management':'jon_management','VCPU':'vcpu','Virt-only':'virt_only','Management Enabled':'management_enabled','Enabled Consumer Types':'enabled_consumer_types','Support Level':'support_level','Required Consumer Type':'requires_consumer_type','Arch':'arch','RAM':'ram','Instance Based Virt Multiplier':'instance_multiplier','Cloud Access Enabled':'cloud_access_enabled','Multi Entitlement':'multi-entitlement','Host Limited':'host_limited','Stacking ID':'stacking_id','Derived SKU':'derived_sku'}

	matched_attribute_name = attribute_dict[attribute]
	return matched_attribute_name

def compare_test_values_with_reference_values(sku, attribute, reference_path):
	logging.info("Begin to verify sku %s attribute '%s' between Reference Doc and Stage Candlepin." %(sku, attribute))

	test_result = True
	#Handle 2013_model types skus
	sku_type = get_sku_type(sku, reference_path)
	attribute_2013_model = ['Instance Based Virt Multiplier','Cloud Access Enabled','Host Limited','Stacking ID','Multi Entitlement','Derived SKU']

	if sku_type == "978418_type" and attribute in attribute_2013_model:
		logging.info("%s - The sku have no the attribute '%s', no need to do the test for the attribute! \n" %(sku, attribute))
	else:
		value_from_reference = get_attribute_value_from_reference(sku, attribute, reference_path)
		value_from_download = get_attribute_value_from_download_data(sku, attribute, reference_path)

		if attribute == "Arch":
			if compare_lists(value_from_reference.lower(), value_from_download.lower()) == False:
                		logging.error("%s - Failed to verify attribute '%s'. \n" %(sku, attribute))
				test_result = False
                	else:
                        	logging.info("%s - It is successful to verify attribute '%s'. \n" %(sku, attribute))
		else:
			if isinstance(value_from_reference, int):
				value_from_reference = str(value_from_reference)

			if isinstance(value_from_download, int):
				value_from_download = str(value_from_download)
				value_from_download = unicode(value_from_download, 'utf-8')

			if (value_from_reference.lower() == value_from_download.lower() or 
                (value_from_reference.lower() in ['0', 'n/a', 'na'] and 
                 value_from_download.lower() in ['0', 'n/a', 'na']) or
                (value_from_reference.lower() in ['1', 'y'] and
                 value_from_download.lower() in ['1', 'y'])):
				logging.info("%s - It is successful to verify attribute '%s'. \n" %(sku, attribute))
			else:
				logging.error("%s - Failed to verify attribute '%s'. \n" %(sku, attribute))
				test_result = False
	return test_result

def compare_lists(r_str, t_str):
        r_list = r_str.replace(' ','').split(',')
        t_list = t_str.replace(' ','').split(',')
        if len(r_list) == len(t_list):
                for i in r_list:
                        if i in t_list:
                                pass
                        else:
                                return False
        else:
                return False

#check the sku type of a sku
def get_sku_type(sku, reference_path):
	refer_dict_lists = []
        refer_dict_lists = eval(open(reference_path).read())
        for i in refer_dict_lists:
        	if i['SKU'] == sku:
                	if i.has_key('Multi Entitlement'):
                        	sku_type = "2013_model_type"
                        else:
                                sku_type = "978418_type"
	return sku_type

#Get sku list according to attribute type
def get_sku_list_by_type(attribute, reference_path):
	attribute_2013_model = ['Instance Based Virt Multiplier','Cloud Access Enabled','Host Limited','Stacking ID','Multi Entitlement','Derived SKU']
	refer_dict_lists = []
        refer_dict_lists = eval(open(reference_path).read())
	sku_list = []
	sku_download_pass_list = get_sku_pass_list_from_file()

	if attribute in attribute_2013_model:
		for dict in refer_dict_lists:
			if dict.has_key(attribute) and dict['SKU'] in sku_download_pass_list:
				sku_list.append(dict['SKU'])
	else:
		#sku_list = get_sku_list_from_reference()
		sku_list = sku_download_pass_list
	return sku_list

def sku_attribute_common(session, params, attribute):
	logging.info("++++++++++++++++++Begin to run SKU attribute: '%s' Test++++++++++++++++++" % attribute)
	auto_client_path = os.environ['AUTODIR']
	reference_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Reference_standard.txt")
	sku_param = params.get("sku")
	test_result = True

	try:
		sku_list = get_sku_list_by_type(attribute, reference_path)

		#get attributes values from reference and download data, then compare them
		failed_sku_list = []
		for sku in sku_list:
			result = compare_test_values_with_reference_values(sku, attribute, reference_path)
			test_result &= result
			if not result:
				failed_sku_list.append(sku)

		if test_result:
			logging.info("It's successful to do sku attribute - '%s' test!" % attribute)
		else:
			logging.info("Failed to do sku attribute test for the following skus: %s" % failed_sku_list)
			raise error.TestFail(" Failed to do sku attribute - '%s' test!" % attribute)

	except Exception,e:
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		logging.info("++++++++++++++++++End to run SKU attribute: '%s' Test+++++++++++++++++++" % attribute)


if __name__=='__main__':
	attribute = 'Cores'

	sku_attribute_common(attribute)
	#get_sku_list_by_type(attribute)

