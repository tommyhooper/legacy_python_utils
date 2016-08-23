#!/usr/bin/python

import time
import sys
import os
import datetime
import commands
import traceback
path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
from A52.Framestore.wiretap import *
from A52.utils import dateutil
from A52.utils import messenger

from optparse import OptionParser
p = OptionParser()
p.add_option("-l",dest='logs', action='store_true',default=False,help="List logs for burn nodes")
options,args = p.parse_args()

def help():
	"""
	Print detailed usage on how to use atempo_delete.
	"""
	text = """usage: burnspy [job_name | batch_name]"""
	print text


if __name__ == '__main__':

	w = Burn(host='backburner')
	if len(sys.argv) > 1:
		j = w.burn_jobs(sys.argv[1])
		if options.logs:
			j.list_logs()
	else:
		w.burn_jobs()
