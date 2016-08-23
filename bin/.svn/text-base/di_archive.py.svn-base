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

from optparse import OptionParser
p = OptionParser()
p.add_option("-c",dest='check', action='store_true',default=False,help="Check if directory has been archived.")
p.add_option("-l",dest='list', action='store_true',default=False,help="List directories in each project that are in the catalog")
#p.add_option("-i",dest='full', action='store_false',default=True,help="Do 'incremental' backup instead of 'full'")
p.add_option("-f",dest='full_only', action='store_true',default=False,help="Only do full archives.")
p.add_option("-n",dest='dry_run', action='store_true',default=False,help="Dry run (do everything but run the archive commands)")
p.add_option("-E",dest='email', action='store_false',default=True,help="Do not send email status")
p.add_option("-y",dest='prompt', action='store_false',default=True,help="Do not prompt before starting archive.")
options,args = p.parse_args()


def send_email(subject,message):
	from_addr = 'eng@a52.com'
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_archive.
	"""
	text = """di_archive directory"""
	print text

def check_archive(path):
	abs_path = os.path.abspath(path)
	obj_path = abs_path.split('DH3723SAS01')[1]
	arch_projects = Tina.tina_find(path_folder=obj_path,application='DI_Archive',strat='A',recursive=False)
	if arch_projects:
		return True
	return False


if __name__ == '__main__':

	if not args:
		help()
		sys.exit()

	if options.check:
		for path in args:
			print "Checking: %s..." % (path),
			if not check_archive(path):
				print "[41mNOT FOUND[m"
			else:
				print "[42mFOUND[m"
		sys.exit()

	if options.list:
		print "List..."
		arch_projects = Tina.tina_find(path_folder="/",application='DI_Archive',strat='A',recursive=False)
		for entry,data in arch_projects.data.iteritems():
			print "ENTRY:",data['path']
			arch_proj_dirs = Tina.tina_find(path_folder=data['path'],application='DI_Archive',strat='A',recursive=False)
			for i,dir_data in arch_proj_dirs.data.iteritems():
				print "\tENTRY:",dir_data['path']
		sys.exit()

	virtual_root = '/Volumes/DH3723SAS01'

	for path in args:
		abs_path = os.path.abspath(path)
		# check for the directory in the catalog
		# in order to set the type of archive
		# correctly: 'full' or 'incr'
		if check_archive(path):
			full = False
			_type = 'incr'
			if options.full_only:
				continue
		else:
			full = True
			_type = 'full'

		# get the full path and strip off the virtual root
		obj_path = abs_path.split('DH3723SAS01')[1]
		print "  Archiving (%s): [33m%s[m" % (_type,obj_path)

		_start = datetime.datetime.today()
		try:
			Tina.backup(obj_path,application='DI_Archive',dry_run=options.dry_run,full=full)
		except KeyboardInterrupt:
			print
			sys.exit()
		except Exception,error:
			traceback.print_exc()
			subject = "Atempo Archive Failed"
			message = "Archive failed for: %s\n" % obj_path
			message += "\nArchive Queue:\n"
			message += "\nEvent log:\n"
			for line in str(error).split('\\n'):
				message += "%s\n" % (line)
			if options.email and not options.dry_run:
				send_email(subject,message)
		else:
			_stop = datetime.datetime.today()
			elapsed = _stop - _start
			print "      [44mComplete:[m Archived %s in %s " % (obj_path,elapsed)
			subject = "DI Archive Complete"
			message = "Archive complete for: %s\n" % obj_path
			message += "Archived %s \n" % (elapsed)
			if options.email and not options.dry_run:
				send_email(subject,message)

	print




