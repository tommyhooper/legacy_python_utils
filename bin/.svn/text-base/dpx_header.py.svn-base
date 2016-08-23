#!/usr/bin/python

import sys
import os
import commands
import glob
import threading
import Queue
import time
import traceback
import re
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
#from A52.utils import messenger
#from A52.utils import fileutil
#from A52.utils import dpx

#import logging
## create a log for the this module
#log = logging.getLogger('PhotomatixCL')
#log_handler = logging.handlers.RotatingFileHandler('/var/log/a52_PhotomatixCL.log','a', 20000000, 100)
#log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
#log_handler.setFormatter(log_format)
#log.addHandler(log_handler)

def help():
	"""
	Print detailed usage on how to use atempo_restore.
	"""
	text = """\nusage: %s <DPX sequence parent folder>\n""" % os.path.split(sys.argv[0])[1]
	print text


if __name__ == '__main__':


	#regx = re.compile('(^.*)_stab.*$')

	if len(sys.argv) == 1:
		help()
		sys.exit()
	for dir in sys.argv[1:]:
		print "Searching in %s" % (dir)
		for dpx in glob.glob("%s/*.dpx" % dir):
			filename = os.path.split(dpx)[1]
			try:
				#tapename = regx.search(filename).group(1)
				tapename = '_'.join(filename.split('_')[0:3])
			except:
				print "[41mError:[m Could not determine tape name for %s" % filename
			else:
				#print "Setting tape name to %s for %s" % (tapename,filename)
				command = "/Volumes/discreet/dev/bin/dpx.py -s input_dev='%s' %s" % (tapename,dpx)
				print command
				commands.getoutput(command)
