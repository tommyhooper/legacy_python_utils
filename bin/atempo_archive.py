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

if os.path.basename(sys.argv[0]) == 'atempo_archive.py':
	ARCH_TYPE = 'archive'
if os.path.basename(sys.argv[0]) == 'atempo_backup.py':
	ARCH_TYPE = 'backup'

from optparse import OptionParser
p = OptionParser()
p.add_option("-n",dest='dry_run', action='store_true',default=False,help="Dry run (do everything but run the tina commands)")
p.add_option("-E",dest='email', action='store_false',default=True,help="Do not send email status")
p.add_option("-y",dest='prompt', action='store_false',default=True,help="Do not prompt before starting the %s." % ARCH_TYPE)
options,args = p.parse_args()


def send_email(subject,message):
	from_addr = 'eng@a52.com'
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_archive.
	"""
	text = """

		      ATEMPO %s v2
			    USAGE:

	%s project [project [project]]...

	
	[44mDirectories:[m
	Only projects in the 'flame_%s' directory will
	be written to tape.
	\n""" % (ARCH_TYPE.upper(),os.path.basename(sys.argv[0]),ARCH_TYPE)
	print text


if __name__ == '__main__':
	
	if not args:
		help()
		sys.exit()

	#print "\n  %-48s%-12s%-18s" % ('Building Queue...','Pool','Status')
	print "\n  %-12s%-18s%-48s" % ( 'Pool', 'Status', 'Building Queue...')
	print "  %s" % ("-"*80)

	arch_queue = []
	ttl_bytes = 0
	for path in args:
		abs_path = os.path.abspath(path)
		if abs_path.split('/')[3] != 'flame_%s' % ARCH_TYPE:
			print "\n[41mERROR[m: Cannot %s %s " % (ARCH_TYPE,abs_path)
			print "       Only projects in the flame_%s directory can be used with this command\n" % (ARCH_TYPE)
			sys.exit()
		DA = DiscreetArchive(abs_path)

		print "  Project: \x1b[38;5;37m%s\x1b[0m" % path
		# get the elements for the project		
		DA.get_elements()
		# print the queue to the console
		DA.print_queue(title=False)
		# add to the total bytes 
		if DA.total_bytes(status='pending') > 0:
			ttl_bytes += DA.total_bytes()
			# add this obj to the queue
			arch_queue.append(DA)

	if not arch_queue:
		print "\n  Nothing to %s. Exiting...\n" % (ARCH_TYPE)
		sys.exit()

	print "\n  Total %s size: %s\n" % (ARCH_TYPE,numberutil.humanize(ttl_bytes,scale='bytes'))

	ri = raw_input("\n  Press [enter] to start the %s." % ARCH_TYPE)
	if ri != "":
		message = "Aborting %s." % (ARCH_TYPE)
		raise Exception,message


	print "\n  %-48s%-12s%-18s" % ('Writing...','Pool','Status')
	print "  %s" % ("-"*80)
	for obj in arch_queue:
		print "  Project: [33m%s[m" % obj.project
		_start = datetime.datetime.today()
		try:
			obj.print_queue(title=False)
			obj._archive(verbose=False,dry_run=options.dry_run)
		except KeyboardInterrupt:
			print
			sys.exit()
		except DLANothingToArchive:
			message = "Nothing to %s.\n" % (ARCH_TYPE)
			print "    [42mNotice:[m %s" % message
		except Exception,error:
			traceback.print_exc()
			subject = "Atempo %s Failed" % (ARCH_TYPE.title())
			message = "%s failed for: %s\n" % (ARCH_TYPE.title(),obj.project)
			message += "\n%s Queue:\n" % (ARCH_TYPE.title())
			for ele in obj.elements:
				message += "  %s\n" % (ele.filename)
			message += "\nEvent log:\n"
			for line in str(error).split('\\n'):
				message += "%s\n" % (line)
			if options.email and not options.dry_run:
				send_email(subject,message)
		else:
			print "      [44mComplete:[m Wrote %s in %s : %s / hour" % (
				obj.archive_size,
				obj.archive_delta,
				obj.archive_rate)
			subject = "Atempo %s Complete" % (ARCH_TYPE.title())
			message = "%s complete for: %s\n" % (ARCH_TYPE.title(),obj.project)
			message += "Wrote %s in %s : %s / hour\n" % (
						obj.archive_size,
						obj.archive_delta,
						obj.archive_rate)
			message += "\n%s Queue:\n" % (ARCH_TYPE.title())
			for ele in sorted(obj.elements, key=lambda x: stringutil.extract_numbers(x.filename)):
				message += "  %s\n" % (ele.filename)
			if options.email and not options.dry_run:
				send_email(subject,message)

	print


