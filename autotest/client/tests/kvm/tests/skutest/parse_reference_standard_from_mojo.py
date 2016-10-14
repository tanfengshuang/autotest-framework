#!/usr/bin/python
import os,sys
from get_https_from_mojo import *
from read_table import *
import getpass
def get_table_data(table_html_dir,\
	     reference_doc_urls,\
             docspace_user,\
             docspace_password,\
             table_html_name,\
             table_txt_dir,\
             table_txt_name,\
             is_wirte_data):

	refer_dict_lists = []

	get_https(table_html_dir, table_html_name, reference_doc_urls, docspace_user, docspace_password)

	refer_dict_lists = read_table(table_html_dir, table_html_name, table_txt_dir, table_txt_name, is_wirte_data)
	#print refer_dict_lists

	print 'Remove file : %s%s ' % (table_html_dir, table_html_name)
	os.remove("%s/%s" % (table_html_dir, table_html_name))

	f = file("./Reference_standard_tmp.txt", 'w')
	str = "%s" % refer_dict_lists
	f.write(str)
	f.close

def modify_attribute_name(reference_path_tmp):
	# modify the table title got from the mojo doc, eg: SKU'id' --> SKU

	f = file("./Reference_standard.txt", 'w')
	data_list = eval(open(reference_path_tmp).read())

	refer_dict_list = []
	for dict in data_list:
		refer_dict = {}
		for key in dict.keys():
			if key.find('\'') >= 0:
				new_key = key.split('\'')[0]
			else:
				new_key = key
			refer_dict[new_key] = dict[key]
		refer_dict_list.append(refer_dict)

	print refer_dict_list
	str = "%s" % refer_dict_list
        f.write(str)
        f.close

	os.remove(reference_path_tmp)


if __name__=='__main__':

	username = ''
	passwd = ''
	if username == '' or passwd == '':
		username = raw_input("Kerberos login: ")
		passwd = getpass.getpass("Kerberos password: ")
	table_html_name = 'table.html'
	table_txt_name = 'table.txt'
	reference_doc_urls = ['DOC-978418','DOC-978431']
	#reference_doc_urls = ['DOC-978418']

	get_table_data('./', reference_doc_urls, username, passwd, table_html_name, './', table_txt_name, False)
	modify_attribute_name('./Reference_standard_tmp.txt')

