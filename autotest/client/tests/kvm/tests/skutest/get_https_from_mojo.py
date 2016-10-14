#!/usr/bin/python
#coding=utf-8

import os
import sys
import requests
from gzip import GzipFile
from cStringIO import StringIO

def get_https_table(table_html_dir, url, login_name, login_passwd):
	s = requests.session()
	s.verify = False

	req = s.get(url, auth=(login_name, login_passwd), headers={'Accept-Language': 'en-US'})
	if req.status_code == 200:
		print "It's successful to log in the url: %s" %url
		all_html = req.content
	else:
		print "Failed to log in the url: %s, the http code is %s, please check the http link." %(url, req.status_code)
		all_html = ""
		
	tbStart_index = all_html.find('DocumentBodyStart') - 6
	print "* Find index for table start ", all_html[tbStart_index:tbStart_index + 65]
	print 'The table start index = %d' % tbStart_index

	# Find the table end like <!-- [DocumentBodyEnd:06e2b56d-a5af-4583-b49b-db35584d0520] -->
	tbEnd_indox = all_html.find('DocumentBodyEnd') + 57
	print "* Find index for table end ", all_html[tbEnd_indox - 63:tbEnd_indox]
	print 'The table end index =%d' % tbEnd_indox

	print '* Cut table content...'
	# cut the table html content to write file
	table_html = all_html[tbStart_index:tbEnd_indox]

	return table_html
	
def get_https(table_html_dir, table_html_name, reference_doc_urls, login_name, login_passwd):

	table_file_path=os.path.join(table_html_dir, table_html_name)
	
	table_file=open(table_file_path, 'w+')
	doc_path = 'https://mojo.redhat.com/docs/'

	for url in reference_doc_urls:
		reference_doc_url = os.path.join(doc_path, url)
		#print reference_doc_url
		table_html = get_https_table(table_html_dir, reference_doc_url, login_name, login_passwd)
		table_file.write(table_html + '\n')
	
	table_file.close()

if __name__=='__main__':
	get_https('./', 'table.html', ['DOC-26756'], 'soliu', '***')

