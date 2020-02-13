#!/usr/bin/python

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 

import time
import sys
import os
import popen2
import datetime
import commands
import traceback
path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
	to_addrs = 'tommy.hooper@a52.com'
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
	to_addrs = 'tina@a52.com'
#from glob import glob
from A52.Atempo import *
from A52.utils import dateutil
from A52.utils import messenger

if not "/dev/" in path:
	# log the command that was run for reference
	command = " ".join(sys.argv)
	Tina.log_command(command)

from optparse import OptionParser
p = OptionParser()
p.add_option("-a",dest='all_volumes', action='store_true',default=False,help="Search all volumes that contain a s+w directory.")
#p.add_option("-E",dest='email', action='store_true',default=True,help="Do not send email status")
options,args = p.parse_args()



def send_email(msg_type,message):
	from_addr = 'eng@a52.com'
	subject = "Tina Restore %s" % msg_type
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_restore.
	"""
	text = """

	usage:  dl_archive_check.py [-a] <volume> [<volume>]
 
        volume    - SAN volume (e.g. QXS648-04)
	    -a        - Search all volumes

	Checks each Flame project found on the specified volume(s)
	for a final archive in the Atempo catalog.

	"""
	print text

if __name__ == '__main__':

	if not args and not options.all_volumes:
		help()
		sys.exit()

	# find all s+w directories
	valid_targets = glob.glob('/Volumes/*/s+w')

	# set the scope of volumes to use
	if options.all_volumes:
		volumes = valid_targets
	else:
		volumes = []
		for vol in args:
			volumes.extend([x for x in valid_targets if vol in x])

	# scan each volume for projects and check
	# for an archive
	i = 0
	for volume in volumes:
		print "Scanning volume:",volume
		for project_path in glob.glob('%s/*' % volume):
			project = os.path.split(project_path)[1]
			print "  Searching for project:",project
			resolved_names = DiscreetArchive.find_project_archived_name(
				project,
				base_dir='flame_archive',
				skip_filter='.offset',
				application='flame_archive',
				full_search=False,
				verbose=False
			)
			if not resolved_names:
				print "    \x1b[38;5;160mNo archive found\x1b[m"
				continue
	
			for archive in resolved_names:
				print '    Scanning archive:',archive



			if i == 1:
				break
			i+=1







