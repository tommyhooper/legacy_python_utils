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
	print "loading dev path..."
	to_addrs = 'tommy.hooper@a52.com'
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
	to_addrs = 'tina@a52.com'
from A52.utils import messenger
from A52.Atempo import *
from A52.utils import dateutil
from A52 import environment
environment.set_context('live')

if not "/dev/" in path:
	# log the command that was run for reference
	command = " ".join(sys.argv)
	Tina.log_command(command)

from optparse import OptionParser
p = OptionParser()
p.add_option("--host",dest='host', type='string',default='tina',help="")
p.add_option("-m",dest='mode', type='string',default=None,help="Consolidation mode: either 'restore' or 'archive'")
p.add_option("-c",dest='cart_limit', type='string',default='5',help="Number of cartridge slots available to use for consolidating.")
p.add_option("-E",dest='email', action='store_false',default=True,help="Do not send email status")
p.add_option("-n",dest='dry_run', action='store_true',default=False,help="Dry run for tina restore / archive commands.")
p.add_option("-a",dest='archive_limit', type='int',default=0,help="Number of archive entries to process.")
#p.add_option("-l",dest='erase_label', type='string',default=None,help="Tape label to check / erase (for erase mode only)")
options,args = p.parse_args()



def help():
	text = """

      ATEMPO CONSOLIDATE USAGE:

  atempo_consolidate [-m mode] [-c cart_limit] [-E (skip email)] [-n (dry run)] [-a archive_limit] [-l erase_label]

      Modes: 

        [33mrestore:[m

            Restores entries from unconsolidated tapes

            The restore process builds a queue of files to restore which
            could potentially be 750 tapes worth so by default the queue
            is limited to 5 tapes worth of files. This can be changed
            using the cart limit argument (-c). 

            Once the queue is built the library is checked to see which
            tapes need to be loaded and a list is given.

            The restores are put in the flame_consolidate directory of the
            current archive array (e.g. /Volumes/flame_archive). They are restored into
            a '.restore' directory then moved in the correct place after the
            restore has finished.

        [33marchive:[m

            Archives entries that have been restored with the 'restore' mode.

            The only thing required for this mode is an ample amount of spare
            tapes to be used for the archive.

        [33merase:[m

            Erases a tape (yes, it's as scary as it sounds)

            There is a bit of safety checking with this mode 
            but still please use with caution.

		Will start at the first tape in the pool unless
		specific tapes are provided on the command line.

        [33mstatus:[m

            Shows progress statistics from the database.


      [42mNOTE:[m
        This process is paranoid. If any errors come up entries are 
        marked in the database as such and skipped. They will continue
	  to be skipped until their status is manually changed in the database.
		
    [44mExamples:[m
      atempo_consolidate -m restore -c 20
      atempo_consolidate -m archive -a 100
      atempo_consolidate -m erase DiscreetArchive0000001 DiscreetArchive0000002


	"""
	print text


def send_email(subject,message,objs=None,error_msg=None,from_addr='eng@a52.com'):
	"""
	Form an email message and send it.
	"""
	# form the email message
	# error first...
	if error_msg:
		message+= "\nError:\n"
		try:
			for line in str(error_msg).split("\n"):
				message+=line
		except:
			message+= "%s\n" % str(error_msg)

	# print the contents of the obj(s) if any
	if objs and type(objs) is not list:
		objs = [objs]
	elif not objs:
		objs = []
	for obj in objs:
		message+= "\n\nObject: %s:\n" % obj
		for k,v in obj.data.iteritems():
			message+= "  %s: %s\n" % (k,v)
	if not options.dry_run:
		if options.email:
			messenger.Email(from_addr,to_addrs,subject,message)

def get_location(cartridges):
	"""
	Get the 'location' from 
	tina_cart_control and set it 
	as an attribute for each cart object.
	"""
	if type(cartridges) is not list:
		cartridges = [cartridges]
	for obj in cartridges:
		info = Tina.get_label_info(obj.data['name'])
		obj.location = info.data['location']

def is_loaded(cartridges):
	"""
	If any cartridge is not loaded
	return False at the end. This function
	doubles as a quick 'yes or no' check
	for a cartridge or list of cartridges.
	"""
	gtg = True
	if type(cartridges) is not list:
		cartridges = [cartridges]
	for tape_id in cartridges:
		info = Tina.get_label_info(tape_id)
		if info.data['location'] == 'External':
			gtg = False
	return gtg

def check_library(cartridges):
	"""
	Check which cartridges are loaded
	and which are not.
	"""
	# set the location for each
	# cart object
	for obj in cartridges:
		get_location(obj)
	loaded = [c.data['barcode'] for c in cartridges if c.location != 'External']
	unloaded = [c.data['barcode'] for c in cartridges if c.location == 'External']
	if loaded:
		print "  The following barcodes are already loaded:"
		loaded.sort()
		for barcode in loaded:
			print "     [42m%s[m" % (barcode)
	if unloaded:
		print "\n  Please load the following barcodes:"
		unloaded.sort()
		for barcode in unloaded:
			print "     [44m%s[m" % (barcode)
	ri = raw_input("\n  Press [enter] when ready ")
	ready = True
	if ri != "":
		sys.exit()

def relocate_restore(csf):
	"""
	Move a restored file out of the 
	temporary restore directory (.consolidate)
	into it's final destination directory.
	"""
	if options.dry_run:
		return True
	
	source = "%s/%s" % (csf.temp_restore_dir,csf.data['filename'])
	dest = "%s/%s" % (csf.final_dest_dir,csf.data['filename'])
	# first check to see if we're overwriting
	# an already existing destination file
	if os.path.exists(dest):
		# form the email message
		subject = "DL Consolidate: Restore failed"
		full_dest = "%s/%s" % (csf.temp_restore_dir,csf.data['filename'])
		message = "Failed to rename: %s\n" % source
		error = "Destination file already exists! %s" % dest
		send_email(subject,message,objs=[csf],error_msg=error)
		if not options.dry_run:
			#csf.data['status'] = 'restore_error'
			csf.data['error_desc'] = message+str(error)
			csf.save()
		raise Exception,error

	try:
		os.rename(source,dest)
	except Exception,error:
		# form the email message
		subject = "DL Consolidate: Restore failed"
		full_dest = "%s/%s" % (csf.temp_restore_dir,csf.data['filename'])
		message = "Failed to rename: %s\n" % source
		send_email(subject,message,objs=[csf],error_msg=error)
		if not options.dry_run:
			#csf.data['status'] = 'restore_error'
			csf.data['error_desc'] = message+str(error)
			csf.save()
		# pass through the exception
		raise
	else:
		# remove the .consolidate directory
		# it gets recreated for each entry
		try: os.removedirs(csf.temp_restore_dir)
		except:
			message = "Could not remove '.consolidate' directory"
			print "    [33mWARNING:[m %s" % message
		return True

def _run_restore(csf):
	"""
	Run the tina_restore and handle 
	nay errors that may occur.
	"""
	try:
		Tina.restore(	path_folder=csf.data['real_path'],
					application=csf.data['real_application'],
					path_dest=csf.temp_restore_dir,
					dry_run=options.dry_run)
	except Exception,error:
		subject = "Atempo Consolidate Error"
		message = 'Restore Failed at: %s' % (dateutil.get_datetime(23))
		send_email(subject,message,objs=[csf],error_msg=error)
		# pass through the exception
		raise

	# the validate routine below only runs
	# if we're not in 'dry-run' mode
	if not options.dry_run:
		return True

	# validate the restored files
	try:
		csf.validate_file_object(path_dest=csf.temp_restore_dir)
	except Exception,error:
		# form the email message
		subject = "DL Consolidate: Restore failed"
		full_dest = "%s/%s" % (csf.temp_restore_dir,csf.data['filename'])
		message = "Could not validate: %s\n" % full_dest
		send_email(subject,message,objs=[csf],error_msg=error)
		# pass through the exception
		raise
	else:
		return True

def validate_restore(csf,stage):
	"""
	Validate the restore file in either 
	of the 2 possible stages:
	'temp' 	- file will be in the '.consolidate'
			  temp directory
	'final'	- file will be in it's final
			  destination directory
	
	If the file is not valid send an email
	with the details then pass through the exception.
	"""
	if stage == 'temp':
		path_dest = csf.temp_restore_dir
	elif stage == 'final':
		path_dest = csf.final_dest_dir

	target = "%s/%s" % (path_dest,csf.data['filename'])
	try:
		csf.validate_file_object(path_dest=path_dest)
	except Exception,error:
		subject = "DL Consolidate: Restore Error"
		if stage == 'temp':
			message = "Error validating file in temp dir: %s\n" % target
		elif stage == 'final':
			message = "Error validating file in final dir: %s\n" % target
		send_email(subject,message,objs=[csf],error_msg=error)
		# pass through (re-raise) the same exception
		raise
	else:
		return True



def Restore():
	"""
	The consolidation restore method.

	This method processes the logic we are using 
	to restore the latest version of a file from 
	the old discreet archive applications to the
	filesystem in preparation for the subsequent
	'archive' (2nd half of the consolidation process)
	"""

	# instantiate the consolidation object
	DC = DiscreetConsolidate()

	print "\n  Generating restore queue"
	print "  ------------------------------------------"
	# finding the latest version is very slow
	# so let's skip that in 'dry run' mode
	if options.dry_run:
		find_latest = False
	else:
		find_latest = True
	
	# generate a restore queue that will require 'x' number
	# of cartridges to be loaded. x = options.cart_limit
	DC.generate_restore_queue(cart_limit=options.cart_limit,find_latest=find_latest)
	ttl_size = numberutil.humanize(DC.restore_queue['ttl_size'],scale='bytes')

	print "\n ","-"*50
	print "  %12s: [33m%s[m" % ('Total Restore Size:',ttl_size)
	print " ","-"*50

	# TODO: if we ever want to use the list options in the tina_restore
	# command we'll need this method. Currently we cannot use this because
	# of a bug in the tina_restore command.
	#DC.create_restore_lists(path_dest=options.path_dest)

	# the tina_restore command does not create it's destination
	# directories so we need to do that for it.
	DC.create_destination_dirs()

	# check for loaded / unloaded cartridges
	print "\n  Barcodes"
	print "  ------------------------------------------"

	# check and show the user what tapes need to be loaded
	# this routine doesn't loop and recheck since there
	# is an option to allow the restore to skip entries
	# who's tape is not loaded (explained below)
	check_library(DC.restore_queue['cartridges'])

	# NOTE: If we use the lists then we'll use the following
	#       command instead of iterating one by one:
	#for app,lists in DC.restore_queue['commands'].iteritems():
	#	try:
	#		Tina.restore(	file_list=lists['filelist'],
	#					dest_list=lists['destlist'],
	#					application=app,
	#					path_dest=options.path_dest)
	print "\n  Restoring"
	print "  ------------------------------------------"
	accm_warn = []
	for csf in DC.restore_queue['objects']:
		carts = [c for c in DC.restore_queue['cartridges'] if c.data['name'] in csf.data['real_tape_ids']]
		# update the location fo the cart (in case someone 
		# removed the cart during a restore
		get_location(carts)

		# I realized that in practice once you load say '20' tapes, you want
		# to keep running the consolidate until you exhaust just about every entry
		# on those tapes without having to constantly load and unload other tapes.
		# ...to that end here we allow skipping entries that do not have their
		# respective cartridges loaded.
		# The down side of this is that we're altering the distribution slightly
		# but I think it's a fair trade.
		missing = [c.data['barcode'] for c in carts if c.location == 'External']
		if missing:
			target = "%s/%s" % (csf.data['parent_dir'],csf.data['filename'])
			message = "Missing tape%s [%s] Skipping: %s" % ('s'*(len(missing)-1),' '.join(missing),target)
			print "  %s" % message
			accm_warn.append(message)
			continue

		print "  %s" % csf.data['real_path'],
		sys.stdout.flush()

		# In case the restore process got interrupted at any point,
		# we check for previous existence of the current file in either
		# the temp directory or it's final destination directory
		# before we run the restore.

		# the 2 places the file may already exist are:
		temp_stage_target = "%s/%s" % (csf.temp_restore_dir,csf.data['filename'])
		final_stage_target = "%s/%s" % (csf.final_dest_dir,csf.data['filename'])

		# if the file is already in the final destination directory,
		# attempt to validate it and mark the db entry accordingly
		if os.path.exists(final_stage_target):
			try: validate_restore(csf,stage='final')
			except Exception,error:
				print "....[31mFAILED[m"
				message = "File already exists in final destination "
				message+= "directory but could not be validated: %s\n" % final_stage_target
				print "    [41mERROR:[m",message
				if not options.dry_run:
					#csf.data['status'] = 'restore_error'
					csf.data['error_desc'] = message+str(error)
					csf.save()
			else:
				print "....[32mOK[m"
				message = "File already exists but is valid."
				print "    [33mWARNING:[m",message
				if not options.dry_run:
					csf.data['status'] = 'restored'
					# we'll store the warning in 'error_desc'
					# even though the entry itself is considered 'restored'
					csf.data['error_desc'] = message
					csf.save()
			# done with this entry
			# so move on to the next...
			continue

		# otherwise if the file is already in the temp restore directory,
		# attempt to validate it, then mark the db entry accordingly
		if os.path.exists(temp_stage_target):
			try: validate_restore(csf,stage='temp')
			except Exception,error:
				print "....[31mFAILED[m"
				message = "File already exists in temp directory "
				message+= "but could not be validated: %s\n" % temp_stage_target
				print "    [41mERROR:[m",message
				if not options.dry_run:
					#csf.data['status'] = 'restore_error'
					csf.data['error_desc'] = message+str(error)
					csf.save()
				# done with this entry
				# move on to the next...
				continue
			else:
				print "....[32mOK[m"
				message = "File already exists but is valid."
				print "    [33mWARNING:[m",message
				# attempt to move this file into place
				try: relocate_restore(csf)
				except Exception,error:
					message = "Could not relocate restored file: %s\n" % temp_stage_target
					print "    [41mERROR:[m",message
					if not options.dry_run:
						#csf.data['status'] = 'restore_error'
						csf.data['error_desc'] = message+str(error)
						csf.save()
				else:
					if not options.dry_run:
						csf.data['status'] = 'restored'
						# we'll store the warning in the error_desc
						# even though the entry is considerred 'complete'
						csf.data['error_desc'] = message
						csf.save()
		else:	
			# create the .consolidation directory
			# (it gets cleaned up after each individual entry)
			# it may already exist so let this command fail
			tmp_dir = "%s/.consolidate" % csf.final_dest_dir
			if not os.path.exists(tmp_dir):
				fileutil.makedirs(csf.temp_restore_dir)
			try: not _run_restore(csf)
			except Exception,error:
				print "....[31mFAILED[m"
				print "\n   [41mERROR:[m",str(error)
				# change the csf entry status 
				# and store the error in the db
				if not options.dry_run:
					#csf.data['status'] = 'restore_error'
					csf.data['error_desc'] = str(error)
					csf.save()
			else:
				print "....[32mOK[m"
				# move the restored file out of the .consolidate directory
				try: relocate_restore(csf)
				except Exception,error:
					message = "Could not relocate restored file: %s\n" % temp_stage_target
					print "    [41mERROR:[m",message
					if not options.dry_run:
						#csf.data['status'] = 'restore_error'
						csf.data['error_desc'] = message+str(error)
						csf.save()
				else:
					subject = "DL Consolidate: Restore complete"
					full_dest = "%s/%s" % (csf.final_dest_dir,csf.data['filename'])
					message = "Restore complete for: %s" % full_dest
					send_email(subject,message)
					if not options.dry_run:
						# change the restore status
						csf.data['status'] = 'restored'
						csf.save()

	if options.email and accm_warn:
		subject = "Atempo Consolidate Warning"
		message = '\nWarning messages:\n'
		message+= "\n".join(accm_warn)
		send_email(subject,message)

	print "\n"

def Archive():
	"""
	The 2nd half of the consolidation effort.
	Once the 'latest' versions of files are restored
	they need to be archived to the new archive pool,
	as well as archived to the new offsite pool.
	"""
	print "\n  %-48s%-18s%-10s" % ('Generating Archive Queue:','Archive Status','Pool')
	print "  %s" % ("-"*80)
	# get the files that are ready from the database
	objects = TinaObject.find(status='restored')
	root = DiscreetArchive.VIRTUAL_ROOT
	i = 1
	ttl_bytes = 0
	obj_queue = []
	for csf in objects:
		# the project directory is always the directory right above the file
		# which in the TinaFind object is the 'parent_dir' 
		project = csf.data['parent_dir']
		year = Tina.parse_year(project)
		path = '%s/flame_consolidate/%s/%s' % (root,year,csf.data['parent_dir'])
		# important to force the 'close' option since all archives
		# in the consolidation are going to the archive pool
		DA = DiscreetArchive(path,close=True)
		if csf.data['filename'] == '.DS_Store':
			print "    [43mWARNING:[m Skipping .DS_Store. Please remove this manually."
			continue
		try:
			DA._get_element(csf.data['filename'])
		except OSError,error:
			print "    [41mError:[m",error
			print "    Resetting status to 'pending'"
			csf.data['status'] = 'pending'
			csf.data['error_desc'] = 'Resetting status to pending. Entry was restored but file is missing.'
			csf.save()
			continue
		# set which pools the file is going to (always archive in our case)
		DA._set_element_pools()
		# see if the file is already in the archive pool
		DA._get_archive_status()
		# print the queue to the console
		DA.print_queue(title=False)
		# add the size to the total if the 
		# archive status is pending
		if DA.elements[0].status == 'pending':
			ttl_bytes += DA.total_bytes()
			# add the DiscreetArchive object to the
			# consolidation file object
			csf.DA = DA
			obj_queue.append(csf)
		elif DA.elements[0].status == 'archived':
			# if the file is already archived then someone
			# or something has beaten us to it and we should
			# mark this entry as such
			csf.data['status'] = 'interceded'
			csf.data['error_desc'] = 'File is already in the archive queue.'
			csf.save()

		# for testing I use this to break
		# out of the loop after a certain
		# number of files
		if options.archive_limit > 0 and i == options.archive_limit:
			break
		i+=1

	ttl_size = numberutil.humanize(ttl_bytes,scale='bytes')
	dbl_size = numberutil.humanize(ttl_bytes*2,scale='bytes')

	if not obj_queue:
		print "\n  [33mWARNING:[m Nothing to archive!"
		return

	print "\n  [41mNOTICE:[m Tape space needed: %s  [%s x 2 pools]" % (dbl_size,ttl_size)
	ri = raw_input("  Press [enter] when ready ")
	if ri != "":
		sys.exit()

	# run the archives
	print "\n  %-48s%-18s%-10s" % ('Archiving:','Archive Status','Pool')
	print "  %s" % ("-"*80)
	for csf in obj_queue:
		csf.DA._get_archive_status()
		ele = csf.DA.elements[0]
		if ele.pool == 'archive' and ele.status == 'archived':
			print "  %s" % ("WARNING: File is already in the archive pool.")
			csf.data['status'] = 'interceded'
			csf.data['error_desc'] = 'File is already in the archive queue.'
			csf.save()
			continue
#		_start = datetime.datetime.today()
		try:
			csf.DA.print_queue(title=False)
			csf.DA._archive(verbose=False,dry_run=options.dry_run)
		except Exception,error:
			traceback.print_exc()
			subject = "DL Consolidate: Archive failed"
			message = "Archive failed for: %s\n" % csf.DA.elements[0].filename
			send_email(subject,message,objs=csf,error_msg=error)
			if not options.dry_run:
				#csf.data['status'] = 'archive_error'
				csf.data['error_desc'] = error
				csf.save()
		else:
			print "      [44mComplete:[m Archived %s in %s : %s / hour" % (
				csf.DA.archive_size,
				csf.DA.archive_delta,
				csf.DA.archive_rate)
			subject = "DL Consolidate: Archive complete"
			message = "Archive complete for: %s\n" % csf.DA.elements[0].filename
			message += "Archived %s in %s : %s / hour\n" % (
				csf.DA.archive_size,
				csf.DA.archive_delta,
				csf.DA.archive_rate)
			send_email(subject,message)
			if not options.dry_run:
				csf.data['status'] = 'archived'
				csf.save()
			# the entry we just archived may change the overall
			# cartridge status so check that here
			for cart_obj in Cartridge.find(name=csf.data['tape_id']):
				cart_obj.update_status()
	
#		_stop = datetime.datetime.today()
#		print "     Elapsed: %s" % (_stop-_start)

		# pause here to let the tina
		# entries complete 
		time.sleep(10)



def Status(pool='Discreet_Archive'):
	"""
	Show the consolidation status.

	TODO: a lot needs to be done with this
	method...

	The idea is to show overall status, 
	or status on a single cartridge etc...
	"""
	#print "\n  STATUS"
	#print "  ------------------------------------------"
	# get the cartridges and separate by status
	carts = Cartridge.find()
	cs = {}
	for cart in carts:
		status = cart.data['status']
		name = cart.data['name']
		try:
			cs[status][name] = cart
		except:
			cs[status] = {name:cart}
	print "\n  [44mBarcode statuses:[m"
	print "  ---------------------"
	for status in cs:
		print "  %10s: %s" % (status,len(cs[status]))
	try:
		pct_complete = round(((float(len(cs['complete'])) / len(carts)))*100,2)
	except:
		pct_complete = 0
	print "  ---------------------"
	print "  %10s: %s (%s%% complete)" % ('Total',len(carts),pct_complete)
	print "\n"
		
	fstats = consolidation_files.status()
	ttl_count = sum([r['count'] for r in fstats])

	print "  %-21s %10s%10s" % ("File statuses",'Count','%')
	print " ","-"*50
	for row in fstats:
		status = row['status']
		count = row['count']
		pct = round((float(count)/ttl_count)*100,2)
		print "  %20s: %10s%10s%%" % (status,count,pct)
		
	print " "



def Check():
	"""
	TEMP method: Checking for previously archived files
	"""
	archive_pool = Tina.tina_find(path_folder='/flame_consolidate',application='flame_archive',strat='A')
	i = 0
	for i,entry in archive_pool.data.iteritems():
		#print entry['path']
		if entry['type'] == 'file':
			base,year,project,filename = entry['path'].split('/')[1:]
			objects = TinaObject.find(relative_path=project,filename=filename)
			obj_sorted = sorted(objects, key=lambda c: c.data['tape_id'])
			if obj_sorted[0].data['status'] == 'pending':
				obj_sorted[0].data['status'] = 'hold'
				print obj_sorted[0].data['path']
				#obj_sorted[0].save()
				i+=1
	print "TOTAL:",i

def Erase():
	"""
	Starts from the first cartridge in
	the old pool, checks all the job id's on 
	that cartridge to make sure the tape can be
	erased.

	DONE:
	R00013 (Discreet_Archive0000001) is erased (but not out of the catalog yet)

	TODO:
	R00015 (Discreet_Archive0000002) can be erased (only mov file left)
	R00032 (Discreet_Archive0000003) can go (only mov file not accounted for).
	R00034 (Discreet_Archive0000004) can go (only mov file left)
	R00037 (Discreet_Archive0000005) can go (only move file left)

	"""


	import logging
	if args:
		labels = args
	#if options.erase_label:
	#	labels = [options.erase_label]
	else:
		print "Getting cart list, this may take a while..."
		pool = Tina.get_pool()
		labels = []
		for i,info in pool.data.iteritems():
			labels.append(info['name'])

	for label in labels:
		# create a log for each tape we're going to erase
		log = logging.getLogger(label)
		log_handler = logging.FileHandler('/var/log/atempo/%s_erase.log' % label,'w')
		log_format = logging.Formatter('[%(asctime)s]: %(message)s','%b %d %H:%M:%S')
		log_handler.setFormatter(log_format)
		log.addHandler(log_handler)
		log.info("ERASE: Checking tape %s" % label)

		# check / erase the tape
		_check_cart(label,log)

def _check_cart(label,log):
	"""
	Check the contents of a cartridge by job_id
	and make sure all entries are expendable.
	"""
	g2g = True
	resolved = False

	# get the barcode for this label
	cart = Cartridge.find(name=label)
	barcode = cart[0].data['barcode']

	print "\n Checking [44m%s (Barcode: %s)[m" % (label,barcode)
	try:
		jids = Tina.tina_listcart(label,job_ids=True)
	except TinaUnknownCartridgeError,message:
		print "\n [41mERROR[m: %s\n" % (message)
		return

	if jids.data == None:
		print "\n  [33mWARNING:[m No job ids found on cart %s." % label
		print "  This is normal if a job id that spans multiple tapes was deleted."
		_erase_cart(label,barcode,log)
		return

	print "  Job ID's:"
	# show the job_ids
	for i in jids.data:
		print "    [44m%(job_id)s[m Backup: %(backup_date)-18s %(strategy)16s %(status)10s" % (jids.data[i])
		log.info("  %(job_id)s Backup: %(backup_date)-18s %(strategy)16s %(status)10s" % (jids.data[i]))

	errors = {}
	_size_mismatch_count = 0
	_scale_mismatch_count = 0
	# loop through the job_ids and check files
	for i in jids.data:
		job_id = jids.data[i]['job_id']
		errors[job_id] = []
		print "\n    Contents of job id [44m%(job_id)s[m: (directories are greyed out)" % (jids.data[i])
		log.info("    Contents of job id %(job_id)s: (directories are greyed out)" % (jids.data[i]))
		jid_obj = Tina.tina_listjob(jids.data[i]['job_id'])
		for x in jid_obj.data:
			info = jid_obj.data[x]
			# if there is more than one cart we have to split the
			# names up since the listjob command just strings them together
			barcodes = []
			for c in range (0,len(info['barcode']),6):
				barcodes.append(info['barcode'][c:c+6])

			if not info['type'] == 'file':
				print "     \x1b[38;5;241m%s: %s %s \x1b[m" % (" ".join(barcodes),info['type'],info['path'])
				log.info("     %s: %s %s " % (" ".join(barcodes),info['type'],info['path']))
			else:
				print "     %s: %s [33m%s[m" % (" ".join(barcodes),info['type'],info['path'])
				log.info("     %s: %s %s" % (" ".join(barcodes),info['type'],info['path']))
				# now find the latest version of this file in the old pool
				try:
					#print "TinaFind.find_latest_archive_segment(",info['path']
					latest = TinaFind.find_latest_archive_segment(info['path'])
				except TinaCatalogOrphanError:
					print "\t\x1b[38;5;124mWarning: Search returned nothing, trying without '-all' flag...\x1b[m"
					latest = TinaFind.find_latest_archive_segment(info['path'],list_all=False)
				except InvalidDLArchivePathError,e:
					log.info("         OLD POOL: NOT FOUND!")
					print "\t[41mWarning:[m %s" % e
					ri = raw_input("\tIf this is ok type 'd' to move on (file will be considered expendable and could end up being deleted): ")
					if ri != "d":
						info['error_desc'] = "File not found in old pool"
						errors[job_id].append(info)
						g2g = False
					continue
				except TinaCompareError,e:
					#print "\t[41mWarning:[m %s" % e

					ri = raw_input("  Type RESOLVED if this problem has been manually resolved:")
					if ri != "RESOLVED":
						g2g = False
						info['error_desc'] = "Date could not be reconciled."
						errors[job_id].append(info)
					else:
						resolved = True
					continue
				
				if latest:
					#print "         Latest version in old pool found on cart(s) %s" % (" ".join(latest['cartridges']))
					# look for the latest version of the file in the new consolidation pool
					tina_obj = TinaObject(**info)
					year = Tina.parse_year(tina_obj.data['parent_dir'])
					if year == 'misc':
						path_year = Tina.parse_year(info['path'])
						if path_year != 'misc':
							year = path_year
					#year = Tina.parse_year(info['path'])
					path_folder = "/flame_consolidate/%s/%s" % (year,tina_obj.data['parent_dir'])
					tf = Tina.tina_find(
						path_folder=path_folder,
						application='flame_archive',
						pattern=tina_obj.data['filename'])
					if not tf or not tf.count or not tf.data:
						print "         NEW POOL: [41mNOT FOUND![m"
						log.info("         NEW POOL: NOT FOUND!")
						g2g = False
						info['error_desc'] = "File not found in new consolidation pool"
						errors[job_id].append(info)
						continue
					_size_mismatch_count = 0
					_scale_mismatch_count = 0
					for i,data in tf.data.iteritems():
						# compare this object against
						# what we found in the new pools:
						print "\tLatest : %10s %2s%19s  (%s)" % (
							latest['size'],
							latest['scale'],
							latest['modification_date'],
							" ".join(latest['cartridges']))
						log.info("       Latest : %10s %2s%19s  (%s)" % (
							latest['size'],
							latest['scale'],
							latest['modification_date'],
							" ".join(latest['cartridges'])))
						#print "\tArchive: %10s %2s%19s" % (data['size'],data['scale'],data['modification_date'])
						log.info("       Archive: %10s %2s%19s" % (data['size'],data['scale'],data['modification_date']))
						print "\tArchive: %10s %2s%19s  (%s) [42mMatched[m" % (	data['size'],
													data['scale'],
													data['modification_date'],
													' '.join(data['cartridges']))
						if data['size'] != latest['size']:
							print "\t[41mSize mismatch:[m %s | %s\n" % (data['size'],latest['size'])
							log.info("\tSize mismatch: %s | %s" % (data['size'],latest['size']))
							_size_mismatch_count+=1
							continue
	
						if data['scale'] != latest['scale']:
							print "\t[41mScale mismatch:[m %s | %s\n" % (data['scale'],latest['scale'])
							log.info("\tScale mismatch: %s | %s" % (data['scale'],latest['scale']))
							_scale_mismatch_count+=1
							continue
				
						if data['modification_date'] != latest['modification_date']:
							print "\t[41mDate mismatch:[m %s | %s\n" % (data['modification_date'],latest['modification_date'])
							log.info("\tDate mismatch: %s | %s" % (data['modification_date'],latest['modification_date']))
							continue
						match = True
						#print "\t[42mMatch:[m Found on cartridge(s): %s\n" % (' '.join(data['cartridges']))
						log.info("       Match: Found on cartridge(s): %s" % (' '.join(data['cartridges'])))
						break
				else:
					print "         OLD POOL: [41mNOT FOUND![m"
					log.info("         OLD POOL: NOT FOUND!")
					info['error_desc'] = "File not found in old pool"
					errors[job_id].append(info)
					g2g = False
					break

		# at this point a job has checked out
		# so we can delete it... permanently (gulp)
		if len(errors[job_id]) == 0 and g2g:
			_delete_job(job_id)

	if _size_mismatch_count > 0:
			print "\n  [43mWARNING![m: There were some size mismatches."
	if _scale_mismatch_count > 0:
			print "\n  [43mWARNING![m: There were some scale mismatches."

	if g2g:
		if resolved:
			print "\n  [41mWARNING![m: Some problems with the contents of this tape have been manually resolved."
			print "  If this tape is erased the manual resolution becomes permanent. Proceed with caution!"
			ri = raw_input("      Type 'go' to continue: ")
			if ri != "go":
				sys.exit()
		_erase_cart(label,barcode,log)
	else:
		log.info("  STOP!: Tape %s cannot be erased." % barcode)
		print "\n  [41mSTOP![m: Tape %s cannot be erased." % barcode
		for job_id,obj in errors.iteritems():
			if len(obj):
				print "    [31mError(s)[m from job id [44m%s[m:" % (job_id)
				for info in obj:
					if type(info) is str:
						print "         %s" % (info)
					else:
						print "     %s: %s [33m%s[m" % (info['barcode'],info['type'],info['path'])
						print "         %s" % (info['error_desc'])
		print "\n"

def _delete_job(job_id):
	"""
	Delete a job from the tina catalog
	"""
	print "\n  [33mWARNING[m: Job ID: %s can be deleted." % (job_id)
	ri = raw_input("  Press 'd' to permanently delete %s from the catalog: " % (job_id))
	if ri != "d":
		print "  Aborting...\n"
		sys.exit()
	Tina.delete_job(job_id)

def _erase_cart(label,barcode,log):
	"""
	Erase a cart (prompt use first)
	"""
	print "\n  [42mOK[m: %s (Barcode: %s) can be erased." % (label,barcode)
	# first check for the barcode in the library:
	while not is_loaded(label):
		print "\n  \x1b[38;5;117mLOAD\x1b[m: Please load cartridge: %s (%s)" % (label,barcode)
		ri = raw_input("  Press [enter] to continue ")
	
	# prompt and erase the tape
	ri = raw_input("  Type 'e' to erase tape. Warning this cannot be undone: ")
	if ri != "e":
		print "  Aborting...\n"
		sys.exit()
	else:
		print "\n  Erasing, please wait..."
		force=False
		while True:
			try:
				Tina.erase_cart(label,force=force)
			except TinaUnselectedRetentionTimeError:
				# try again with -force
				force = True
				print "  Adding -force option..."
			except TinaWriteProtectError:
				print "\n  [41mERROR[m: %s is write protected." % (barcode)
				time.sleep(5)
				return
			except:
				print "  Error erasing tape, please check the logs."
				return
			else:
				print "  Offlining cartridge..."
				# offline the cart:
				Tina.offline_cart(barcode)
				print "  Done. Please remove tape %s from the library."  % barcode
				# form the email message
				subject = "DL Consolidate: %s erased" % (barcode)
				message = "Cartridge %s was erased and has been offlined.\n" % barcode
				message+= "Please remove it from the library, it should be in the mailbox.\n"
				message+= "\n(Label: %s)\n" % label
				send_email(subject,message)
				break
			




if __name__ == '__main__':
	
	# STATUSES: (consolidation_files table)
	#	
	# Normal chain of events:
	#
	#	pending		- nothing has been done yet to this file
	#	restored		- latest file has been restored to the filesystem
	#	backup		- file was archived to the new backup pool but has not been validated
	#				  not sure if we need this status
	#	archived		- file was archived to the new pools but has not been validated
	#	validated 		- file has been validated against the new pool
	#
	#
	# Abnormal conditions:
	#
	#	hold			- only used to temporarily exclude entries (dev only)
	#	duplicate		- only the first instance of a file in the database is used 
	#				  to track the statuses of the consolidation. Remaining 
	#				  instances of the same file are listed as 'duplicate'
	#	interceded		- the file is found in the new archive pool before the
	#				  consolidation had a chance to archive it there.
	#	skip			- there are several entries that are not going to the
	#				  new archive pool... e.g. the NY setup files
	#	invalid_path	- A 'correct' entry for a discreet archive always
	#				  follows the same naming convention:
	#				  /<top level directory>/<project directory>/<segment or header file>
	#				  when an entry does not follow this convention it is marked
	#				  as 'invalid_path'


	# STATUSES: (consolidation_pools table)
	#
	#	pending		- tape is in progress
	#	hold			- tape is ignored (dev)
	#	complete		- all entries have been consolidated



	from_addr = 'eng@a52.com'

	#print "------------------------------------------"
	#print "            ATEMPO CONSOLIDATE            "
	#print "------------------------------------------"

	if options.mode == 'restore':
		Restore()
	elif options.mode == 'archive':
		Archive()
	elif options.mode == 'status':
		Status()
	elif options.mode == 'check':
		Check()
	elif options.mode == 'erase':
		Erase()
	else:
		help()
