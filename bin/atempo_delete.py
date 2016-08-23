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
from A52.Atempo import *
from A52.utils import dateutil
from A52.utils import messenger

if not "/dev/" in path:
	# log the command that was run for reference
	command = " ".join(sys.argv)
	Tina.log_command(command)

from optparse import OptionParser
p = OptionParser()
p.add_option("-g",dest='gut', action='store_true',default=False,help="Delete all but the last segment and header.")
p.add_option("-f",dest='force', action='store_true',default=False,help="Force delete segments that have not yet been written to tape.")
options,args = p.parse_args()

def send_email(subject,message):
	from_addr = 'eng@a52.com'
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_delete.
	"""
	text = """

		      ATEMPO DELETE USAGE:

	atempo_delete project [project [project]]...

	* project must be a valid path
	  (relative or absolute)

	[44mExamples:[m
	     atempo_delete flame_backup/2012/12A104_ASICS_DC_1_DA
	     atempo_delete flame_archive/2012/12A104_ASICS_DC_1_DA
	     atempo_delete /Volumes/F6412SATA01/flame_archive/2012/12A104_ASICS_DC_1_DA

	NOTE: This command will only delete files that have been written to tape. 
	      In order to delete files that have not been written to tape you must 
		use the '-f' option.

	[41mWARNING:[m
		The command by default will delete ALL segments AND the header.
		If you want to leave the last segment and header you must 
		use the '-g' option.

	"""
	print text



if __name__ == '__main__':

	if not args:
		help()
		sys.exit()

	print "\n%2s%-50s%-12s%-18s%-10s%-16s" % (' ','Filename: (* is last segment)','Pool','Archive Status','Size','Delete')
	print "  %s" % ("-"*96)
	del_st_size = 0
	keep_st_size = 0
	del_obj_queue = []
	for project in args:
		path = os.path.abspath(project)
		DA = DiscreetArchive(path)
		DA.get_elements()
		print "  Project: [33m%s[m" % path
		if not DA.elements:
			continue
		last_seg = DA.last_segment()
		first_seg = DA.first_segment()

		for ele in DA.elements:
			save = False
			# previous to 2016.2.1 segment 1 needed
			# to exist in order for the flame to 
			# recognize an archive and show it in 
			# the browser. That is no longer necessary
			# so I'm commenting out the segment 1 exception:
			#if ele == first_seg:
			#	if options.gut:
			#		save = True
			if ele == last_seg:
				name = "%s*" % ele.filename
				if options.gut:
					save = True
			else:
				name = ele.filename

			if ele.element_type == 'header' and options.gut:
				save = True

			if ele.status=='archived' and not save:
				del_st_size+=ele.st_size
				size = numberutil.humanize(ele.st_size,scale='bytes')
				print "%4s%-48s%-12s%-18s%-10s\x1b[31m%-16s\x1b[m" % (
					" ",
					name,
					ele.pool,
					ele.status,
					size,
					'DELETE')
				del_obj_queue.append(ele)
			elif ele.status=='pending' and options.force and not save:
				del_st_size+=ele.st_size
				size = numberutil.humanize(ele.st_size,scale='bytes')
				print "%4s%-48s%-12s%-18s%-10s\x1b[31m%-16s\x1b[m" % (
					" ",
					name,
					ele.pool,
					ele.status,
					size,
					'DELETE')
				del_obj_queue.append(ele)
			elif ele.status=='pending' and ele.pool=='backup' and not save:
				del_st_size+=ele.st_size
				size = numberutil.humanize(ele.st_size,scale='bytes')
				#print "%4s%-48s%-12s\x1b[38;5;124m%-18s\x1b[m%-10s\x1b[33m%-16s\x1b[m" % (
				print "%4s%-48s%-12s\x1b[38;5;124m%-18s\x1b[m%-10s%-16s" % (
					" ",
					name,
					ele.pool,
					ele.status,
					size,
					'KEEP')
				#del_obj_queue.append(ele)
			else:
				# \033[38;5;8m
				keep_st_size+=ele.st_size
				size = numberutil.humanize(ele.st_size,scale='bytes')
				print "\x1b[38;5;241m%4s%-48s%-12s%-18s%-10s%-16s\x1b[m" % (
					" ",
					name,
					ele.pool,
					ele.status,
					size,
					'KEEP')
	print "\n  Totals"
	print " ","-"*50
	print "  %12s: %s" % ('Delete',numberutil.humanize(del_st_size,scale='bytes'))
	print "  %12s: %s" % ('Keep',numberutil.humanize(keep_st_size,scale='bytes'))
	print " ","-"*50
	print "  %12s: %s\n" % ('Total',numberutil.humanize(del_st_size + keep_st_size,scale='bytes'))

	if len(del_obj_queue):
		ri = raw_input("\n  Press [enter] to delete segments marked above.")
		if ri != "":
			message = "Aborting..."
			raise Exception,message
	else:
		print "\n  Nothing to delete. Exiting...\n"
		sys.exit()


	for obj in del_obj_queue:
		print "     [31mDeleting:[m %s" % (obj.target)
		os.remove(obj.target)
		# CLEAN UP: attempt to remove the project directory
		# and the year* directory.
		# * remove the .DS_Store file in the year directory
		#   leftover from mac browsing
		project_dir = os.path.split(obj.target)[0]
		year_dir = os.path.split(project_dir)[0]
		for _dir in [project_dir,year_dir]:
			ds = "%s/.DS_Store" % _dir
			try: os.remove(ds)
			except: pass
			try: os.removedirs(_dir)
			except: pass




