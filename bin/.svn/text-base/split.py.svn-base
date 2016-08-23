#!/usr/bin/python

import sys
import os
import commands
import glob
import threading
import Queue
import time
import traceback
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import messenger
from A52.utils import fileutil

import logging
# create a log for the this module
log = logging.getLogger('PhotomatixCL')
log_handler = logging.handlers.RotatingFileHandler('/var/log/a52_PhotomatixCL.log','a', 20000000, 100)
log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
log_handler.setFormatter(log_format)
log.addHandler(log_handler)


def groups(data,length):
	"""
	Iterate through 'data'
	by groups of 'length'
	"""
	for i in xrange(0,len(data),length):
		yield data[i:i+length]



if __name__ == '__main__':

	for d in ['bracket_01','bracket_02','bracket_03']:
		try:
			os.makedirs(d)
		except:
			#traceback.print_exc()
			pass

	files = glob.glob('*.tif')
	i = 1
	for x,y,z in groups(sorted(files),3):
		print "-"*50
		print "\t",x
		print "\t",y
		print "\t",z
		target = 'img.%04d.tif' % i
		print "os.symlink(",x,'bracket_01/%s' % target
		print "os.symlink(",y,'bracket_02/%s' % target
		print "os.symlink(",z,'bracket_03/%s' % target
		os.symlink("../%s" % x,'bracket_01/%s' % target)
		os.symlink("../%s" % y,'bracket_02/%s' % target)
		os.symlink("../%s" % z,'bracket_03/%s' % target)

		i+=1



