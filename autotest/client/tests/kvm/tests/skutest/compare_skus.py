import re
import logging
from autotest_lib.client.common_lib import error

def get_skus_from_reference_doc(path):
	file = open(path)
	lists = eval(file.read())
	sku_list = []
	for dict in lists:
		sku_list.append(dict['SKU'])

	sku_list.sort()
	sku_list = list(set(sku_list))

	length = len(sku_list)
	logging.info("**********************************************************************************************")
	logging.info("The list get from reference doc is: %s" % sku_list)

	return sku_list
		

def get_skus_from_regression_code(path):
	file = open(path)
	skus = file.read().split(' ')
	sku_list = []
	for list in skus:
		list = list.replace('tc_SKU_', '')
		sku_list.append(list)
	
	length = len(sku_list) - 1
	sku_list[length] = sku_list[length].replace('\n', '')
	
	sku_list.sort()
	return sku_list

def strip_blank_item_in_list(list):
	new_list = []
	for l in list:
		if l != '':
			new_list.append(l)
	return new_list

def find_start_number_of_sku_in_list(str, list):
	i = 0		
	for l in list:
		i = i+1
	     	if "tc_SKU" in l:
             		break
	start_number = i - 1
	return start_number

def get_skus_from_regression_code2(path):
	file = open(path)
	lists = file.readlines()
	sku_lists = lists[3].split(" ")
	strip_blank_item_in_list(sku_lists)
	
	sku_str = "tc_SKU_"
	
	start_item = find_start_number_of_sku_in_list(sku_str, sku_lists)
	end_item = len(sku_lists) 
	sku_lists = sku_lists[start_item:end_item]

	new_sku_list = []
	for l in sku_lists:
		if (sku_str in l) and ("consistency" not in l) and ("regression_result" not in l):
			l = l.replace(sku_str,'')
			l = l.replace('\n','')
			new_sku_list.append(l)
	new_sku_list = list(set(new_sku_list))
	new_sku_list.sort()

	logging.info("The list get from regression code is: %s" %new_sku_list)
	return new_sku_list

def compare_list(list1, list2):
	test_result = True

	in_list1_not_in_list2 = []
	in_list2_not_in_list1 = []
	test_list = []

	for list in list1:
		if list not in list2:
			in_list1_not_in_list2.append(list)

	for list in list2:
		if list not in list1:
			in_list2_not_in_list1.append(list)
		else:
			test_list.append(list)
	length = len(test_list)

	if in_list1_not_in_list2 == [] and in_list2_not_in_list1 == []:
		print "The two list are the same!"
		return test_result
	else:
		print "Following item exist in list1 but not exist in list2: %s" %in_list1_not_in_list2
		print "Following item exist in list2 but not exist in list1: %s" %in_list2_not_in_list1
		test_result = False
		return test_result

def compare_two_lists(list1, list2):
	test_result = True

	list1_length = len(list1)
        list2_length = len(list2)

        if list1_length == list2_length:
                print "The sku number is the same between reference doc and regression code! "
                test_result &= compare_list(list1, list2)
        else:
                print "The sku number in reference doc is %s" %list1_length
                print "The sku number in regression code is %s" %list2_length
                print "The sku number is not the same between reference doc and regression code!"
                test_result &= compare_list(list1, list2)

	if test_result:
		logging.info("It is successfull to verify the sku consistency!")
	else:
		logging.error("Failed to verify the sku consistency!")

	return test_result

def analysis_list(list):
	MCT_list = []
	RH_list = []
	MW_list = []
	other_list = []

	for l in list:
		if "MCT" in l:
			MCT_list.append(l)
		else:
			if "RH" in l:
				RH_list.append(l)
			else:
				if "MW" in l:
					MW_list.append(l)
				else:
					other_list.append(l)

	print "The number of RH_list is %s, the list is %s" %(len(RH_list), RH_list)
	print "The number of MCT_list is %s, the list is %s" %(len(MCT_list), MCT_list)
	print "The number of MW_list is %s, the list is %s" %(len(MW_list), MW_list)
	print "The number of other_list is %s, the list is %s" %(len(other_list), other_list)

def skus_consistency_test(regression_path, reference_path):
	"""verify the skus consistency between sku regression code and reference doc-95917"""
	test_result = True

	try:
		sku_list_regression = get_skus_from_regression_code2(regression_path)
		sku_list_reference = get_skus_from_reference_doc(reference_path)
		test_result &= compare_two_lists(sku_list_regression, sku_list_reference)
		if not test_result:
			raise error.TestFail("Test Failed - Failed to do sku consistency testing!")
	except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do SKU Consistency testing:"+str(e))
