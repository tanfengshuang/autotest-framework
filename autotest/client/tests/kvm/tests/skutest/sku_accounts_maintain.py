import re,os
import logging
#from autotest_lib.client.common_lib import error

def get_info_from_reference_doc(path):
	file = open(path)
	lists = eval(file.read())

	directory_path = os.environ['PWD']
        stage_accounts_tmp_path = os.path.join(directory_path, "StageTestingSKUs_tmp.csv")
	stage_accounts_path = os.path.join(directory_path, "AllStageTestingSKUs.csv")

	if os.path.exists(stage_accounts_path):
		os.remove(stage_accounts_path)
	
	sku = ''
	stage_account = ''
	total_info = ''
	stage_account_list = []
	
	for dict in lists:
		sku = dict['SKU']
		stage_account = dict['Username']
		if stage_account not in stage_account_list:
			stage_account_list.append(stage_account)
		#	total_info = sku + ',1000,'
		#	print total_info
			 
		#else:
		#stage_account_list.append(stage_account)
 		total_info = '\n' + stage_account + ',redhat,' + sku + ',1000,'
		print total_info

		file_tmp = open(stage_accounts_tmp_path, "a")
		if total_info != '\n':
                	file_tmp.write(total_info)
                file_tmp.close

	#Handle those same stage account issue

	file_tmp = open(stage_accounts_tmp_path)
	file = open(stage_accounts_path, "a")
	lists = file_tmp.readlines()
	
	for stage_account in stage_account_list:
		test = ''
		for list in lists:
			account = list.split(',')[0]
			if stage_account == account:
				test += list.split(',')[2] + ',' + list.split(',')[3] + ','
		test = stage_account + ',redhat,' + test + ',,,\n'
		print test
		file.write(test)
	
	os.remove(stage_accounts_tmp_path)		 
	print "+++++++++++++++++++++++++"

	'''	
	length_lists = len(lists)

	for l in lists:
		if l != '\n':
			newlist = l.replace(',\n', ',,,,\n')
			file.write(newlist)
	
	lists[length_lists - 1] = lists[length_lists - 1] + ",,,"
	file.write(lists[length_lists - 1]) 
	file.close

	os.remove(stage_accounts_tmp_path)

	print stage_account_list	
	'''
	
if __name__== "__main__":

	directory_path = os.environ['PWD']
	reference_doc_path = os.path.join(directory_path, "Reference_standard.txt")

	get_info_from_reference_doc(reference_doc_path)
