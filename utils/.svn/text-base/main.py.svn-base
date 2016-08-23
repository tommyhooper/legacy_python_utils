#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import os
import sys
import types
import re
import datetime
import traceback

def dbg(message,log_level=0):
	"""
	Global control of debug messages
	"""
	env = os.getenv('FUSE_DEBUG')
	if not env: return
	try:
		if int(env) >= log_level:
			now = datetime.datetime.now()
			timestamp = datetime.datetime.strftime(now,'%d/%m/%y %H:%M:%S')
			if type(message).__name__ == 'dict':
				print "[%s]%s: Dict:" % (log_level,timestamp)
				print_array(message)
			else:
				print "[%s] %s  %s" % (log_level,timestamp,message)
	except:pass

def print_array(array,tab=0):
	# iterate through an array until the keys are exhausted
	# are there any keys?
	indexes = array.keys()
	indexes.sort()
	for i in indexes:
		# is the value another array? check here
		if type(array[i]) is dict:
			# it is an array... print the key, and spawn this function again to print the next level of the array
			print "%s * %s =>" % ('\t'*tab,i)
			print_array(array[i],tab=tab+1)
		else:
			# it is not an array - just print the key and the value
			print "%s + %s => %s" % ('\t'*tab,i,array[i])

# convenient way to list the contents of an object
def inspect(obj,filter='dict'):
	"""
	print object info
	"""
	print "[44mOBJECT >>>[m"
	if filter == 'full':
		index = {}
		for key in dir(obj):
			key_type = type(eval("obj.%s" % key))
			try:
				index[key_type][key] = eval("obj.%s" % key)
			except:
				index[key_type] = {key:eval("obj.%s" % key)}
		A52.utils.print_array(index)
		return 1
	else:
		index = {}
		for key in dir(obj):
			key_type = type(eval("obj.%s" % key))
			if key_type is dict:
				try:
					index[key_type][key] = eval("obj.%s" % key)
				except:
					index[key_type] = {key:eval("obj.%s" % key)}
		A52.utils.print_array(index)
		return 1
       

if __name__ == '__main__':
	pass



