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
p.add_option("-n",dest='get_size', action='store_false',default=True,help="Skip calculating size of archive. This will speed up the search considerably. This disables the show all option (-a).")
p.add_option("-v",dest='verbose', action='store_true',default=False,help="Verbose: Show details for the files used for modification date and backup date.")
p.add_option("-a",dest='show_all', action='store_true',default=False,help="Show all: Show archive contents.")
options,args = p.parse_args()


def send_email(subject,message):
	from_addr = 'eng@a52.com'
	messenger.Email(from_addr,to_addrs,subject,message)

def help():
	"""
	Print detailed usage on how to use atempo_archive.
	"""
	text = """usage: nas_project [options] project[s]
	
	options:
		-h, --help  show this help message and exit
		-n          Skip calculating size of archive. This will speed up the search considerably. This disables the show all option (-a).
		-v          Verbose: Show details for the files used for modification date and backup date.
		-a          Show all: Show archive contents.

	
	
	"""
	print text

def check_project_for_archive(project,get_size=False,verbose=False,show_all=False):
	"""
	Search for a CG project archive
	#o = a.tina_find(path_folder='/A_to_backup/12A212_google_knowing',application='nas0-taylor.a52.com.fs',list_all=True,recursive=True)
	"""
	print "\x1b[48;5;236m"
	print "\n\x1b[38;5;255mSearching for \x1b[38;5;255m%s..." % project,
	sys.stdout.flush()
	nas0_search_path = '/A_to_backup/%s' % project
	nas2_search_path = '/E_to_backup/%s' % project
	# note recursive options follows the get_size flag
	nas0_search = Tina.tina_find(path_folder=nas0_search_path,application='nas0-taylor.a52.com.fs',recursive=get_size,list_all=False)
	nas2_search = Tina.tina_find(path_folder=nas2_search_path,application='nas2-taylor.a52.com.fs',recursive=get_size,list_all=False)

	for search in [nas0_search,nas2_search]:
		if search.found_status == TinaFind.FOUND_SET_MATCH:
			print " \x1b[38;5;2mFound"
			if show_all:
				if not get_size:
					print "[31mWARNING: Cannot use -n and -a together (try removing -n)\n\n[m"
					return
				print "\x1b[38;5;208mArchive Contents:"
				for k,v in search.data.iteritems():
					if v['type'] == 'dir':
						print "   \x1b[38;5;67m%s: \x1b[38;5;102m%s/%s" % (v['modification_date'],v['base_path'],v['filename'])
					elif v['type'] == 'file':
						print "   \x1b[38;5;67m%s: \x1b[38;5;102m%s/\x1b[38;5;252m%s" % (v['modification_date'],v['base_path'],v['filename'])
			if get_size:
				print "   \x1b[38;5;2mArchive Size:",
				sys.stdout.flush()
				search.find_size()
				print "\x1b[38;5;255m%s" % search.found_size_human
			max_mod_obj,max_bak_obj = search.newest()
			print "   \x1b[38;5;208mLatest modification date: \x1b[38;5;255m%s" % max_mod_obj['modification_date']
			if verbose:
				for k,v in max_mod_obj.iteritems():
					print "      \x1b[38;5;208m%s: \x1b[38;5;255m%s" % (k,v)
			print "   \x1b[38;5;208mLatest backup date:       \x1b[38;5;255m%s" % max_bak_obj['backup_date']
			if verbose:
				for k,v in max_bak_obj.iteritems():
					print "      \x1b[38;5;208m%s: \x1b[38;5;255m%s" % (k,v)
			return True
		#elif search.found_status == TinaFind.FOUND_SET_EMPTY:
		#	print "[31mProject not archived[m"
		#	return TinaFind.FOUND_SET_EMPTY
		elif search.found_status == TinaFind.FOUND_SET_ERROR:
			print "Error searching for project"
			return TinaFind.FOUND_SET_ERROR
		#elif search.found_status == TinaFind.FOUND_SET_NONE:
		#	print "Search never executed"
		#	return TinaFind.FOUND_SET_NONE
	print "[31mProject not archived[m"




if __name__ == '__main__':

	if not args:
		help()
		sys.exit()

	for project in args:
		check_project_for_archive(project,get_size=options.get_size,verbose=options.verbose,show_all=options.show_all)
	print "\x1b[0m"




