#!/usr/bin/python
import os,sys
from get_https import *
from read_table import *
def get_table_data(table_html_dir,\
             reference_doc_url,\
             docspace_user,\
             docspace_password,\
             basic_realm,\
             table_html_name,\
             table_txt_dir,\
             table_txt_name,\
             is_wirte_data):

    # Get Reference documentation table
    get_https(table_html_dir,reference_doc_url,docspace_user,docspace_password,basic_realm)

    # Parse Reference documentation table - get target values ...
    refer_dict_lists=[]
    refer_dict_lists=read_table(table_html_dir,table_html_name,table_txt_dir,table_txt_name,is_wirte_data)
    Reference_stadard_path='./Reference_standard2.txt'
    # write file
    f=file(Reference_stadard_path,'w')
    str='%s' %refer_dict_lists
    print '* Write dict list to %s' %Reference_stadard_path
    f.write(str)
    f.close()

if __name__=='__main__':
    # call function sku_test
    get_table_data(
             './' ,\
             'https://docspace.corp.redhat.com/docs/DOC-95917' ,\
             'xhe' ,\
             '123456' ,\
             'Red Hat Login' ,\
             'table.html' ,\
             './' ,\
             'table.txt' ,\
             True
             )

