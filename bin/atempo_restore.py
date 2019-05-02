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
p.add_option("-s",dest='start_seg', type='int',help="Segment number to start at. For restoring a specific range or specific segment.")
p.add_option("-e",dest='end_seg', type='int',help="Segment number to end at. For restoring a specific range or specific segment.")
p.add_option("-a",dest='dest_array', type='string',default=None,help="The array restores will be written to.")
p.add_option("-E",dest='email', action='store_true',default=True,help="Do not send email status")
p.add_option("-c",dest='seg_count', type='int',default=None,help="Number of segements to restore starting with the last segment first. Useful for restoring the last 'x' segments.")
p.add_option("-b",dest='flame_backup', action='store_true',default=False,help="Use flame_backup instead of flame_archive for restores.")
p.add_option("-i",dest='in_place', action='store_true',default=False,help="Restore files in place instead of to 'holding'")
p.add_option("-f",dest='full_search', action='store_true',default=False,help="Search all year folders for a project (default search year corresponding to a project job number: 19A100 = 2019)")
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

		      ATEMPO RESTORE USAGE:

	atempo_restore  project [project [project]]...

	Restores Flame archive segments and headers to 
	the 'holding' directory on the current archive array.

	[44mProject names:[m
	Project names do not have to be complete. For example
	you can specify just the job number (e.g. 11A123)

	Each project name will be resolved against the Tina
	catalog. If multiple results are found they are 
	printed in the console and the command will exit.
	If this happens you will need to re-run the command
	using one of the names in the list.

	[44mSegment range:[m
	If you want a specific segment, or a range of 
	segments you can use the -s (start) and -e (end)
	arguements. For example:

	atempo_restore -s 5 -e 7 11A123

	  ... will restore segments 5,6 and 7 of job
	      11A123

	atempo_restore -s 3 -e 3 11A123

	  ... will restore segment 3 job 11A123

	[41mOverwriting files:[m
	Files that already exist on the filesystem are
	skipped automatically. 
	
	* If you want restore a file that exists you 
  	  will have to move or rename the file that is 
	  already on the filesystem.

	[44m'holding' directory:[m
	In order to restore files back into the 'flame_archive' 
	directory instead of the holding directory you must use 
	the in-place option '-i'. This option is dangerous so 
	only use it if you know what you are doing.

	[44m'flame_backup' directory:[m
	In the rare case that you need to restore something 
	from 'flame_backup' you must use the '-b' option.
	This will switch the restore completely to the 
	'flame_backup' directory meaning nothing will be
	searched in either the old archives or the 
	'flame_archive' directory. Restores from
	'flame_backup' do not go into 'holding' and
	instead go back into 'flame_backup'.
	"""
	print text

if __name__ == '__main__':

	if not args:
		help()
		sys.exit()


	if not options.dest_array:
		options.dest_array = DiscreetArchive.VIRTUAL_ROOT

	if options.flame_backup:
		application = 'flame_backup'
		base_dir = 'flame_backup'
		strat = 'B'
		dest_path = '%s/%s/restore' % (options.dest_array,base_dir)
	else:
		application = 'flame_archive'
		base_dir = 'flame_archive'
		strat = 'A'
		if options.in_place:
			dest_path = '%s/%s' % (options.dest_array,base_dir)
		else:
			dest_path = '%s/holding' % (options.dest_array)

	# show where we're restoring to
	print "\n  \x1b[38;5;43mRestore path set to:\x1b[m %s" % dest_path

	# resolve the project name(s)
	abort = False
	project_names = []
	for project in args:
		print "\n  Resolving project name: %s: " % project
		sys.stdout.flush()
		resolved_names = DiscreetArchive.find_project_archived_name(
			project,
			base_dir=base_dir,
			skip_filter='.offset',
			application=application,
			full_search=options.full_search,
			verbose=True
		)
		if project in resolved_names:
			# found an exact match
			#print "[42m%s[m" % (project)
			print "       * [44m%s[m" % (project)
			project_names.append(project)
		elif len(resolved_names) == 1:
			#print "[42m%s[m" % (resolved_names[0])
			print "       * [44m%s[m" % (resolved_names[0])
			project_names.append(resolved_names[0])
		elif len(resolved_names) > 1:
			print "      [31mWarning:[m Multiple names found for %s:" % project
			for name in resolved_names:
				print "       * [44m%s[m" % (name)
			print "      Please specify one of these on the command line.\n"
			sys.exit()
		else:
			print "\n\n      [41mWarning:[m No projects found matching: %s" % project
			sys.exit()

	# build a restore queue
	queue = []
	carts = []
	segx = re.compile('.*_([0-9]*).seg$')
	for project in project_names:
		year = Tina.parse_year(project)
		path = "%s/%s/%s/%s" % (DiscreetArchive.VIRTUAL_ROOT,base_dir,year,project)
		path_folder = "/%s/%s/%s" % (base_dir,year,project)

		if base_dir == 'flame_archive':
			# check to see if this 'flame_archive' project shows up in the 'B' strategy
			# At some point the flame_archive directory was archived into the B strategy
			# which can cause some restore issues we want to make a warning for.
			#search_results = DiscreetArchive(path)._get_project_tina_entries(pool='backup',refresh=True)
			obj = Tina.tina_find(
				path_folder=path_folder,
				application='flame_archive',
				strat='B',
				skip_filter='.offset')
			if obj.found_status == TinaFind.FOUND_SET_MATCH:
				print "\n  [41mWARNING:[m 1 or more elements of this 'flame_archive' project show up in the backup strategy."
				print "  (There should never be a 'flame_archive' path in the backup strategy, but it happens)"
				print "  There have been instances of this where the 'latest' version of an archive was"
				print "  corrupt and the paths that found their way into the backup strategy were needed."
				print "  Please scrutinize and verify the contents of this restore very carefully.\n"
				print "  [33mPATHS:[m Here are the suspicious paths:"
				for x,y in obj.data.iteritems():
					print "    %s" % (y['path'])
					for i,v in y.iteritems():
						print "        [33m%s[m: %s" % (i,v)
					#print_array(y)
				print ""
				ri = raw_input("  Press [enter] when ready ")
				if ri != "":
					sys.exit()

		found = {}
		print "\n  Getting files for: [42m%s[m" % project
		search_results = DiscreetArchive(
			path,
			skip_filter='.offset',
			application=application
			).find_archived_project_files(
				search_old_apps=True,
				search_consolidate=True
			)
		if not search_results:
			print "\nCould not find %s\n" % project
			sys.exit()

		# narrow the restore list if 
		# the '-c' option was used
		#print "\n  Restore list:"
		print " ","-"*50
		headers = [v for i,v in search_results.iteritems() if v['path'][-4:] != '.seg']
		all_segs = [v for i,v in search_results.iteritems() if v['path'][-4:] == '.seg']
		all_segs = sorted(all_segs,key=lambda x: stringutil.extract_numbers(x['path']))
		if options.seg_count == 0:
			segments = []
		elif options.seg_count > 0:
			if len(all_segs) > options.seg_count:
				segments = all_segs[options.seg_count*-1:]
			else:
				segments = all_segs
		elif options.start_seg:
			segments = [s for s in all_segs if int(segx.search(s['path']).group(1)) >= options.start_seg]
			if options.end_seg:
				segments = [s for s in segments if int(segx.search(s['path']).group(1)) <= options.end_seg]
		else:
			segments = all_segs

		# filter out existing segments and headers
		# and print the restore queue to the console
		filtered = []
		for f in headers + sorted(segments, key=lambda x: stringutil.extract_numbers(x['filename']),reverse=True):
			if f['filename'] == '.DS_Store':
				continue
			year = Tina.parse_year("%s/%s" % (f['parent_dir'],f['filename']))

			f['path_dest'] = "%s/%s/%s" % (dest_path,year,project)
			f['filename'] = os.path.split(f['path'])[1]
			f['target'] = "%s/%s" % (f['path_dest'],f['filename'])
			f['temp_target'] = "%s/.restore/%s" % (f['path_dest'],f['filename'])
			print "  %s..." % (f['path']),
			sys.stdout.flush()
			time.sleep(.05)
			if os.path.exists(f['target']):
				print "[41mSkipping[m (file exists)"
			elif os.path.exists(f['temp_target']):
				print "\n\n  [41mError[m This file exists in the temporary restore location."
				print "     This means either a previous attempt to restore this file failed, "
				print "     or there is a restore currently running for this file."
				print "     This problem needs to be rectified manually before we can proceed."
				print "     The path of the temporary file is:"
				print "\n     %s\n" % f['temp_target']
				sys.exit()
			else:
				print "[44mRestoring[m"
				filtered.append(f)
			time.sleep(.02)
		queue += filtered


	if len(queue) == 0:
		# nothing to restore
		print "\n  Nothing to restore. Exiting...\n"
		sys.exit()

	# check the library for unloaded tapes
	ready = False
	print "\n  Searching for barcodes..."
	
	while not ready:
		# resolve labels into barcodes 
		labels = {}
		for label_list in [v['cartridges'] for v in queue]:
			for label in label_list:
				if 'off' not in label and not labels.has_key(label):
					obj = Tina.get_label_info(label)
					print "    %-20s-->  %-12s %s" % (label,obj.data['barcode'],obj.data['location'])
					labels[label] = obj.data
	
		external = []
		internal = []
		for label,info in labels.iteritems():
			if info['location'] == 'External' and not info['barcode'] in external:
				external.append(info['barcode'])
			elif info['location'] not in internal:
				internal.append(info['barcode'])
			
		if internal:
			external.sort()
			print "\n  The following barcodes are already loaded:"
			print " ","-"*50
			for barcode in internal:
				print " ",barcode
		if external:
			external.sort()
			print "\n  Please load the following barcodes:"
			print " ","-"*50
			for barcode in external:
				print "  [44m%s[m" % (barcode)
			ri = raw_input("  Press [enter] when ready ")
			print "  Rescanning barcodes..."
			if ri == "go":
				ready = True
			elif ri != "":
				sys.exit()
		else:
			#print "\tAll cartridges are loaded."
			ready = True

	# once we're set to go ask for one last 'enter' 
	# (one last chance to cancel)
	ri = raw_input("  All barcodes found... hit [enter] to start restore. ")
	if ri != "":
		sys.exit()

	print "\n  Restoring..."
	print " ","-"*50
	# run the restores
	i = 1
	for entry in queue:
		appl = Tina().APPLICATIONS[entry['application']]
		tmp_path_dest = "%s/.restore" % (entry['path_dest'])
		if not os.path.exists(tmp_path_dest):
			os.makedirs(tmp_path_dest)
		print "  Restoring (%s of %s): %s" % (i,len(queue),entry['target'])
		try:
			#print "Tina.restore(path_folder=%s,application=%s,path_dest=%s,strat='%s')" % (entry['path'],appl,tmp_path_dest,strat)
			Tina.restore(path_folder=entry['path'],application=appl,path_dest=tmp_path_dest,strat=strat)
		except Exception,error:
			message = 'Restore of: %s\n' % entry['path']
			message+= 'Resting to: %s\n' % entry['target']
			message+= 'Failed at: %s' % (dateutil.get_datetime(23))
			message+= '\nError message:\n'
			for line in error.message.split("\n"):
				message+= '%s\n' % line
			if options.email:
				send_email('Failed',message)
			#else:
			#	traceback.print_exc()
			#	print message
			print "\n[41mError running tina command:[m"
			print "%s\n" % message
		else:
			# move the restored file out of the .restore directory
			source = "%s/%s" % (tmp_path_dest,entry['filename'])
			target = entry['target']
			#print "os.rename(",source,target
			os.rename(source,target)
			try:
				os.removedirs(tmp_path_dest)
			except:pass

			# send off the success message
			message = 'Restore of: %s\n' % entry['target']
			message+= 'Completed at: %s' % (dateutil.get_datetime(23))
			if options.email:
				send_email('Complete',message)
		i+=1




