#!/usr/bin/env python

import urllib
import re

APIKEY = {	'a52':"LmFGV29XYESTQJARVWIwK",
		'elastic':"20kquxQwwrRDuF1xy0asx",
		'rps':""}

class Interdubs:
	"""
	Wrapper class for the InterDubs API
	"""
	def __init__(self,company='a52'):
		# the regex for splitting key,value 
		# pairs in the output from the API
		self.re = re.compile('^([A-Z0-9_]*):(.*)$')
		self.apikey = APIKEY[company]

	def _url(self,function=None,**kwargs):
		# we build the URL that builds the request
		url = "http://www.interdubs.com/api/"
		url += "?idxapi_key=%s" % (self.apikey)
		url += "&idxapi_function=%s" % (function)
		for k,v in kwargs.iteritems():
			url+="&%s=%s" % (k,v)
		return url

	def _send(self,url):
		f = urllib.urlopen(url)
		s = f.read()
		f.close
		return s

	def _convert_status(self,status):
		if status == 'IDXAPI_OK':
			return True
		elif status == 'IDXAPI_SIMOK':
			return True
		elif status == 'IDXAPI_ERROR':
			return False 
		elif status == 'IDXAPI_FAILURE':
			return False 

	def _parse(self,output):
		# first line is always status
		# the function is not important for now
		status,function = self._parse_line(output.split('\n')[0])
		i = 1
		result = {}
		for line in output.split('\n')[1:]:
			key,value = self._parse_line(line)
			result[i] = (key,value)
			i+=1
		return (self._convert_status(status),result)

	def _parse_line(self,line):
		if line == '':
			return (None,None)
		try:
			key,value = re.match(self.re,line).groups()
		except:
			print "Unable to parse line: %s" % line
			return (None,None)
		return (key,value)

	def poll(self,**kwargs):
		url = self._url(**kwargs)
		result = self._send(url)
		return self._parse(result)

	def list_logins(self):
		result = self.poll(function='list_logins')
		print result

	def list_jobs(self):
		result = self.poll(function='list_jobs')
		print result

	def create_folder(self,folder,parent_id=1):
		print "Creating interdubs folder: %s" % folder
		return self.poll(function='create_folder',idxapi_par1=folder,idxapi_par2=parent_id)

	def create_subfolder(self,parent_folder,subfolder):
		print "Creating interdubs subfolder: %s/%s" % (parent_folder,subfolder)
		url_return = self.poll(function='list_node_ids',idxapi_par1=parent_folder,idxapi_par2=1)
		node_id = None
		if url_return[0] == True:
			print url_return[1]
			for k,v in url_return[1].iteritems():
				if v[0] == 'IDXAPI_NODE_IDS_ID':
					node_id = v[1].strip()
					break
		if node_id:
			print "node_id: (%s)" % node_id
			return self.poll(function='create_folder',idxapi_par1=subfolder,idxapi_par2=node_id)
		

if __name__ == '__main__':
	i = Interdubs()
#	i.list_logins()
#	i.list_jobs()
#	i.create_folder('api_test')
	print i.create_subfolder('14A131_Android_Wear','test_02')
# 	14A125_Ford_Purpose = 67519
#	14A108_MSFT_Olympics = 64499
#	14A131_Android_Wear = 68058

#	WORKING EXAMPLE:
#	1. get folder id:
#		http://www.interdubs.com/api/?idxapi_key=LmFGV29XYESTQJARVWIwK&idxapi_function=list_node_ids&idxapi_par2=1&idxapi_par1=14A131_Android_Wear
#		returns node_id: 68058
#	2. create folder
#		http://www.interdubs.com/api/?idxapi_key=LmFGV29XYESTQJARVWIwK&idxapi_function=create_folder&idxapi_par1=test_01&idxapi_par2=68058
	pass



