#!/usr/bin/python

import sys
import os
import commands
import glob
import time
import traceback
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import messenger

import logging
# create a log for the this module
log = logging.getLogger('PhotomatixCL')
log_handler = logging.handlers.RotatingFileHandler('/var/log/a52_PhotomatixCL.log','a', 20000000, 100)
log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
log_handler.setFormatter(log_format)
log.addHandler(log_handler)

def help():
	"""
	Print detailed usage on how to use atempo_restore.
	"""
	text = """\nusage: %s <CR2 image file directory or directories>\n
		""" % os.path.split(sys.argv[0])[1]
	print text

def groups(data,length):
	"""
	Iterate through 'data'
	by groups of 'length'
	"""
	for i in xrange(0,len(data),length):
		yield data[i:i+length]

def find_cr2_images(path):
	"""
	Walk the 'path' and find CR2 files.
	Return a dictionary in this form:
		{'path to cr2 sequence': [list of cr2 files]}
	"""
	images = {}
	for root,dirs,files in os.walk(path):
		for _file in files:
			if _file[-3:].lower() == "cr2":
				try:
					images[root].append(_file)
				except:
					images[root] = [_file]
	return images

def form_destination_path(source_path,tail_directories=2):
	"""
	Form the destination path based on the given
	'source_path' using the last 'x' number
	of directories at the END of the path.
	The default is to use the last 2 directories
	in the path but this can be changed by 
	using the 'tail_directories' argument.
	"""
	split = source_path.split('/')
	raw_index = split.index('raw')
	dest_head = "%s/exr" % ("/".join(split[0:raw_index]))
	dest_tail = "/".join(split[-tail_directories:])
	return "%s/%s" % (dest_head,dest_tail)


if __name__ == '__main__':

	if len(sys.argv) < 2:
		help()
		sys.exit()

	# build the queue for the processing threads
	for path in sys.argv[1:]:
		# convert the path to absolute
		abs_path = os.path.abspath(path)

		# search for cr2 files
		print "Scanning path for CR2 files: %s" % path
		search = find_cr2_images(abs_path)

		# iterate through the found images
		for source_path in sorted(search):
			print "[44m%s[m" % source_path
			images = search[source_path]

			# process in groups of 3s
			images.sort()
			frame_count  = 0
			for group in groups(images,3):
				frame_count+=1
				outfile = '%04d.exr' % (frame_count)
				print "  %s: %s" % (outfile,' '.join(group))




