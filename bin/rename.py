#!/usr/bin/python

import time
import sys
import os
#import popen2
import datetime
import commands
import traceback

from optparse import OptionParser
p = OptionParser()
p.add_option("-f",dest='force', action='store_true',default=False,help="Force rename when infile and outfile templates are the same.")
#p.add_option("--host",dest='host', type='string',default='tina',help="")
#p.add_option("-m",dest='mode', type='string',default='restore',help="Consolidation mode: either 'restore' or 'archive'")
#p.add_option("-c",dest='cart_limit', type='string',default='5',help="Number of cartridge slots available to use for consolidating.")
p.add_option("-d",dest='dry_run', action='store_true',default=False,help="Dry run. Print what would be renamed but don't rename anything.")
#p.add_option("-a",dest='archive_limit', type='int',default=0,help="Number of archive entries to process.")
options,args = p.parse_args()

def help():
	
	print """
		
		RENAME
	
	usage: rename infile_template outfile_template start end [new_start] [-f]

	Infile and outfile templates are in 'printf' format and should be 
	expressed either as aboslute paths or relative from where you
	execute the script. Replace the frame number portion of the filename
	with %0Xd where 'X' is the number of digits (padding) in the number... 
	e.g. 0001 is 4 digits so the padding is 4 and would be expressed as %04d.

	Examples:

	somefile.000001.exr  	= somefile.%06d.exr
	somefile.0001.exr  	= somefile.%04d.exr
	somefile.01.exr		= somefile.%02d.exr
	somefile.1.exr		= somefile.%01d.exr

	If the infile template and the outfile templates are
	the same the script will complain and exit unless you 
	force it to do the rename with the -f option. The only
	time this is ever used is to change the start and end
	however if the 'new_start' number is higher then you
	have the potential to overwrite existing files as you
	rename them.

	"""


def check_file_template(template):
	"""
	Check that the file template is in 
	an acceptable printf format.
	"""
	try:
		testfile = template % 1
	except:
		#traceback.print_exc()
		return False
	return True



if __name__ == '__main__':

	if not args or len(args) < 4:
		help()
		sys.exit()
	
	infile_template = args[0]
	outfile_template = args[1]
	start = int(args[2])
	end = int(args[3])
	if len(args) == 5:
		newstart = int(args[4])
	else:
		newstart = start

	cwd = os.path.abspath(os.curdir)
	# determine the absolute path to the files
	if infile_template[0] != '/':
		# relative path was given (or just the filename
		# which is effectively the same
		abs_infile_template = "%s/%s" % (cwd,infile_template)
	else:
		abs_infile_template = infile_template

	if outfile_template[0] != '/':
		# relative path was given (or just the filename
		# which is effectively the same
		abs_outfile_template = "%s/%s" % (cwd,outfile_template)
	else:
		abs_outfile_template = outfile_template


	# check the infile template format
	if not check_file_template(abs_infile_template):
		print "Error in infile template format."
		sys.exit()

	# check the outfile template format
	if not check_file_template(abs_outfile_template):
		print "Error in infile template format."
		sys.exit()

	# check that all the source frames exist
	for i in range(start,end+1,1):
		target = abs_infile_template % i
		if not os.path.exists(target):
			print "Error: missing frame: %s" % target
			#sys.exit()

	# check if the infile template matches the
	# outfile template
	if abs_infile_template == abs_outfile_template:
		# they can match as long as the
		# new_start is > end
		if newstart < end and not options.force:
			print "Error: infile and outfile templates match. (use -f to force the rename)"
			sys.exit()
	
	offset = newstart - start
	for i in range(start,end+1,1):
		infile = abs_infile_template % i
		outfile = abs_outfile_template % (i+offset)
		if os.path.exists(outfile):
			if not options.force:
				print "Error: outfile already exists. Exiting."
				sys.exit()
		else:
			if options.dry_run:
				print "DRY RUN: Renaming: %s -> %s" % (infile,outfile)
			else:
				print "Renaming: %s -> %s" % (infile,outfile)
				os.rename(infile,outfile)


	




