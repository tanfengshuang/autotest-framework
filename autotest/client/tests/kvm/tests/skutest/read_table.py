import os,sys
from HTMLParser import HTMLParser
import copy
import time
import logging
from htmlentitydefs import *

def get_local_time():
	timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	return timestr

class MyHTMLParser(HTMLParser):

	def __init__(self, myfile, is_write_file, filename, dtlist):
		HTMLParser.__init__(self)
		
		self.myfile = myfile
		self.is_write_file = is_write_file
		self.filename = filename
		self.dtlist = dtlist
		self.dt = {}
		self.headlist = []
		self.row = -1
		self.col = -1
		self.data = ''
		self.MAX_COLUMNS = -1	#define the max columns, it will increase 1 everty time read a head list from table
	
		print self.myfile
		print self.filename
		print self.is_write_file

		if self.is_write_file == True:
			string = '* Open %s\n' % self.filename
			print string
        
	def handle_starttag(self, tag, attrs):
		if tag == 'tr':
			self.row = self.row + 1
			self.col = -1
			if self.is_write_file == True:
				wStr = '==== Row %d ====\n' % self.row
				print wStr
				self.myfile.write(wStr)
		elif tag == 'td':
			self.col = self.col + 1
		elif tag == 'table':
			string = 'Target table: <table>'
			print string

	def handle_endtag(self, tag):
		if tag == 'table':
			print "Encountered an table end tag:%s\n" % tag

		if tag == 'td':
        		#print "Encountered an cell end tag: %s\n" % tag
			if self.row == 1:
                        	self.headlist.append(self.data)
                        	self.MAX_COLUMNS = self.MAX_COLUMNS + 1

			if self.row > 1:
			#if 1 < self.row < 154 or self.row > 188:
				self.dt[self.headlist[self.col]] = unicode(self.data, 'utf-8')

				if self.col == self.MAX_COLUMNS:
					self.dtlist.append(self.dt)
					self.dt = {}

			wStr = 'row = %d col = %d: %s\n' % (self.row, self.col, self.data)
			print wStr
			if self.is_write_file == True:
				self.myfile.write(wStr)
			self.data = ''

	def handle_data(self, data):

		if self.row == 1:
			self.data = self.data + data
			string = '* Get table header : %s' % data
			print string
	
		if self.row > 1:
			self.data = self.data + data
	
	def handle_entityref(self, name):
		# handle special charactors, such as &ndash; &mdash; 
		print "--- handle_entityref: %s ---" % name
		if name2codepoint.has_key(name):
			special_data = unichr(name2codepoint[name]).encode('utf-8')
			print "special charactor: &%s;  and its normal display: %s" % (name, special_data)
			self.handle_data(special_data)
		else:
			self.handle_data('&'+name+';')
			print "other special charactor &%s; " % name
 
	def handle_charref(self, name):
		# handle special charactors, such as &#8211;
		print "--- handle_charref: %s ---" % name
		name = int(name)
		if name in name2codepoint.values():
			special_data = unichr(name).encode('utf-8')
			print "special charactor: &#%s;  and its normal display: %s" % (name, special_data)
			self.handle_data(special_data)
		else:
			self.handle_data('&#'+name+';')
			print "other special charactor &#%s; " % name

	def handle_comment(self, data):
		string = "Comment  :", data 
		print string
		if data.find('DocumentBodyEnd') >= 0:
			string = '* List the valid sku attributes...\n'
			print string
			string = '* Done table read! Totel sku %d!\n' %len(self.dtlist)
			print string

	def handle_decl(self,data):
		string = "Decl     :", data
		print string

def uniqueList(L):  
	(output, temp) = ([],[])  
	for l in L:  
		for v, k in l.iteritems():  
			flag = False  
			if (k,v) not in temp:  
				flag = True  
				break  
		if flag:  
			output.append(l)
		temp.extend(l.items())  
	return output  

def read_table(table_html_dir, table_html_name, table_dir, output_table_name, is_write_file):
	mydictlist = []

	table_file_path = os.path.join(table_html_dir, table_html_name)
	output_table_path = os.path.join(table_dir, output_table_name)
	
	htmlfile = file(table_file_path, 'r')
	all_text_lines = htmlfile.readlines()
	
	# get file handle   
	fileHd = file(output_table_path, 'w')

	for line in all_text_lines:
		print line
		ret = line.find('DocumentBodyStart')
		if ret >= 0:
			parser = MyHTMLParser(fileHd, is_write_file, output_table_path, mydictlist)
			parser.feed(line)
			parser.close()	
	fileHd.close()
	htmlfile.close()
	    	
	if not is_write_file:
		os.remove(output_table_path)
	    
	return mydictlist

