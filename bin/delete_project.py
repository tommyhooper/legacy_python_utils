#!/usr/bin/python

import time
import sys
import os
import popen2
import datetime
import commands
import traceback
exe_path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in exe_path:
	print "Loading dev path"
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
	to_addrs = 'tommy.hooper@a52.com'
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
	to_addrs = 'tina@a52.com'
from A52.Atempo import *
from A52.utils import dateutil
from A52.utils import messenger

if not "/dev/" in exe_path:
	# log the command that was run for reference
	command = " ".join(sys.argv)
	Tina.log_command(command)

from optparse import OptionParser
p = OptionParser()
p.add_option("-a",dest='all', action='store_true',default=False,help="Search for all tina objects (-all option for tina_find)")
p.add_option("-E",dest='email', action='store_false',default=True,help="Do not send email status")
#p.add_option("-y",dest='prompt', action='store_false',default=True,help="Do not prompt before starting the %s." % ARCH_TYPE)
options,args = p.parse_args()


def send_email(subject,message):
	from_addr = 'eng@a52.com'
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_archive.
	"""
	text = """

		      DELETE_PROJECT
			    USAGE:

	%s project [project [project]]...

	
	\n""" % (os.path.basename(sys.argv[0]))
	print text


if __name__ == '__main__':
	
	if not args:
		help()
		sys.exit()

#	print "\n  %-48s%-12s%-18s" % ('Building Queue...','Pool','Status')
#	print "  %s" % ("-"*80)

	arch_queue = []
	ttl_bytes = 0
	for project in args:
		print "  Project: [33m%s[m" % project




