

######################################
# 
# DL Archive tools.
#	
# Strategy:
#	The main context of an archive is the project level.
#	Within a project each segment	is determined to be either
#	"open" 	- segments that are still being appended to
#	"closed" 	- segement is not going to be appended to.
#			  this is for the final segment in an archive 
#			  when an archive is complete
#
#	Based on this classification segements are archived
#	into either the backup pool or the archive pool
#		"open"   segments are the only segments that 
#		         actually ever go to the backup pool
#		"closed" segments are archived into the archive pool
#	
#	
######################################

from tina import *
import glob
import re
import os
import time
from datetime import datetime
from A52.utils import fileutil
from models import consolidation_pools
from models import consolidation_files

import logging
log = logging.getLogger(__name__)


			
class DLANothingToArchive(Exception):


	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)


class DLAProjectNotFound(Exception):


	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)



class DiscreetArchive:

	# APPLICATION = 'Discreet_2010_Archive'
	# STRAT_PATH = 'hoop_test'
	OLD_APPS = {	'tina.a52.com.fs':['/2007_archive','/2008_archive','/2009_archive','/2010_archive','/archive'],
				'Discreet_2010_Archive':['/2010_archive'],
				'Discreet_2011_Archive':['/2011_archive'],
				}
	VIRTUAL_ROOT = '/Volumes/MD3860'

	def __init__(	self,
				path=None,
				virtual_root=VIRTUAL_ROOT,
				application='flame_archive',
				close=False,
				skip_filter=None):
		self.allow_base_dirs = ['flame_archive','flame_backup','flame_consolidate']
		self.virtual_root = virtual_root
		self.application = application
		self.close = close
		self.skip_filter = skip_filter
		self._parse_path(path)

		# list to store elements contained within
		# this archive object
		self.elements = []

		# status color codes
		#self.status_cc = {	'archived':32,
		#				'pending':33,
		#				'unknown':33,
		#				}
		self.status_cc = {	'archived':34,
						'pending':208,
						'unknown':171,
						}
		# archive stats to store actual
		# execution time, size & rate
		self.archive_delta = None
		self.archive_seconds = 0
		self.archive_bytes = 0
		self.archive_size = 0
		self.archive_rate = 0
	
	def _parse_path(self,path):
		"""
		Split the path into required parts.

		/Volumes/flame_archive/flame_backup/2012/12A777-some_project
		"""
		split = path.split('/')
		if len(split) != 6:
			message = 'Invalid archive path: %s' % path
			raise Exception,message

		root = '/'.join(split[0:3])
		if root != self.virtual_root:
			message = 'Root must be %s (%s)' % (self.virtual_root,path)
#			raise Exception,message

		self.base_dir = split[3]
		if self.base_dir not in self.allow_base_dirs:
			message = "Base directory (%s) must be one of: %s" % (self.base_dir,self.allow_base_dirs)
			raise Exception,message

		self.year = split[4]
		self.parent_dir = self.year
		self.project = split[5]

		self.segment_path = "%s/%s/%s/%s" % (
			self.virtual_root,
			self.base_dir,
			self.parent_dir,
			self.project
			)
		self.catalog_path = "/%s/%s/%s" % (
			self.base_dir,
			self.parent_dir,
			self.project
			)

		self.catalog_paths = {}
		for _dir in self.allow_base_dirs:
			self.catalog_paths[_dir] = "/%s/%s/%s" % (_dir,self.parent_dir,self.project)

	def __getattr__(self,name):
		if name == "archive_queue":
			return self.generate_queue('archive')
		if name == "backup_queue":
			return self.generate_queue('backup')
		if name == "headers":
			return [h for h in self.elements if h.element_type=='header']
		if name == "segments":
			return [s for s in self.elements if s.element_type=='segment']
		message = "'%s' object has no attribute '%s'" % (__name__,name)
		raise AttributeError,message

	def create_project_folder(self):
		"""
		Create the project folder in 
		the correct year directory.
		"""
		if not os.path.exists(self.segment_path):
			fileutil.makedirs(self.segment_path)

	def archive(self,prompt=True,dry_run=False):
		"""
		Main method to process the archiving
		of the project.
		"""
		# make sure the project is valid
		self.validate_project()

		# get the segments
		self.get_segments()

		# get the header file(s)
		self.get_headers()

		# determine which pool each file is going to
		self._set_element_pools()

		# check the files against the pools for duplicates
		self._get_archive_status()

		# print what we found for archiving
		self.print_queue()

		# check to see if we have anything to archive
		# and prompt the user 
		self.ready_check(prompt=prompt)

		# do the archive
		self._archive(dry_run=dry_run)

	def validate_project(self):
		"""
		Check for the existence of the project
		in it's proper location.
		"""
		if not os.path.exists(self.segment_path):
			error = "%s does not exist" % self.segment_path
			raise DLAProjectNotFound,error

	def ready_check(self,prompt=True):
		"""
		Check to see if 
		"""
		if len([e for e in self.elements if e.status=='pending' and e.pool != 'unknown']) == 0:
			message = "Nothing to archive."
			#print "  [42mNotice:[m %s" % message
			raise DLANothingToArchive,message
		# prompt before beginning what could potentially
		# be a very long archive
		if prompt:
			ri = raw_input("\n  Press [enter] to start the archive.")
			if ri != "":
				message = "Aborting archive."
				raise Exception,message
		return True

	def print_queue(self,title=True):
		seg_sort = sorted(self.segments, key=lambda x: stringutil.extract_numbers(x.filename))
		hdr_sort = sorted(self.headers, key=lambda x: x.filename)
		if title:
			#print "  \x1b[m%-48s%-12s%-18s" % ("[44m%s[m" % self.project,'Pool','Archive Status')
			m = "    %-10s" % 'Pool'
			m+= "%-27s" % 'Archive Status'
			m+= "\x1b[38;5;45m%-48s\x1b[0m" % self.project
			print m
			print "  %s" % ("-"*80)
		for hdr in hdr_sort:
			if hdr.status == 'archived':
				status = 'on tape'
			else:
				status = hdr.status
			size = numberutil.humanize(hdr.st_size,scale='bytes')
			m = "    %-10s" % hdr.pool
			m+= '\x1b[38;5;%dm%-14s\x1b[0m' %  (self.status_cc[hdr.status],status)
			m+= "\x1b[38;5;%dm[\x1b[0m%s\x1b[38;5;%dm]\x1b[0m %-48s" % (self.status_cc[hdr.status],size,self.status_cc[hdr.status],hdr.filename)
			print m
		for seg in seg_sort:
			if seg.status == 'archived':
				status = 'on tape'
			else:
				status = seg.status
			size = numberutil.humanize(seg.st_size,scale='bytes')
			m = "    %-10s" % seg.pool
			m+= '\x1b[38;5;%dm%-14s\x1b[0m' % (self.status_cc[seg.status],status)
			m+= "\x1b[38;5;%dm[\x1b[0m%s\x1b[38;5;%dm]\x1b[0m %-48s" % (self.status_cc[seg.status],size,self.status_cc[seg.status],seg.filename)
			print m


	def total_bytes(self,pool=None,status=None):
		"""
		Add up the total bytes of both queues
		"""
		ttl = 0
		for ele in self.elements:
			if pool and ele.pool not in pool:
				continue
			if status and ele.status not in status:
				continue
			ttl+=ele.st_size
		return ttl

	def get_headers(self):
		"""
		Grab segments from the project's 
		archive path
		"""
		# collect all the non-segment
		# files into a list (there
		# should only be one header)
		files = glob.glob("%s/*" % self.segment_path)
		headers = [f for f in files if os.path.splitext(f)[1] != '.seg']
		for path in headers:
			_file = os.path.split(path)[1]
			dae = DiscreetArchiveElement(self,_file,element_type='header')
			self.elements.append(dae)
		return True

	def get_segments(self):
		"""
		Grab segments from the project's 
		archive path
		"""
		os.chdir(self.segment_path)
		for path in glob.glob("%s/*.seg" % self.segment_path):
			_file = os.path.split(path)[1]
			dae = DiscreetArchiveElement(self,_file,element_type='segment')
			self.elements.append(dae)
		return True
	
	def last_segment(self):
		"""
		Return the last segment stored
		in the object.
		"""
		seg_sort = sorted(self.segments, key=lambda x: stringutil.extract_numbers(x.filename))
		if seg_sort:
			return seg_sort[-1]
		else:
			return None
	
	def first_segment(self):
		"""
		Return the first segment stored
		in the object.
		"""
		seg_sort = sorted(self.segments, key=lambda x: stringutil.extract_numbers(x.filename))
		if seg_sort:
			return seg_sort[0]
		else:
			return None

	def get_elements(self):
		"""
		Grab a specific element (file) 
		from the project's archive path
		"""
		if not os.path.exists(self.segment_path):
			return False
		for path in glob.glob("%s/*" % self.segment_path):
			_file = os.path.split(path)[1]
			# ignore core dumps from TiNa
			if _file[:5] == 'core.':
				continue
			# ignore save files
			if _file.rstrip('1234567890')[-5:] == '_save':
				continue
			if _file[-4:] == '.seg':
				_type = 'segment'
			else:
				_type = 'header'
			dae = DiscreetArchiveElement(self,_file,element_type=_type)
			self.elements.append(dae)
		# set which pools each file is going to
		self._set_element_pools()
		# see if each file is already in the archive pool
		self._get_archive_status()
		return True

	def _get_element(self,filename):
		"""
		Grab a specific element (file) 
		from the project's archive path
		"""
		target = "%s/%s" % (self.segment_path,filename)
		if not os.path.exists(target):
			message = "No such file or directory: %s" % target
			raise OSError,message
		if target[-4:] == '.seg':
			_type = 'segment'
		else:
			_type = 'header'
		dae = DiscreetArchiveElement(self,filename,element_type=_type)
		self.elements.append(dae)
		return True

	def _get_archive_status(self):
		"""
		Get each elements archive status by looking
		at the contents of the pool they are set to.

		When a segment is going to the archive pool, a search for 
		an exact match is done first to avoid duplication. If there is
		a different version of a segment is should be smaller and have
		an older modification date.

		For the backup pool we can do the same search but only 
		to save time since duplication is not an issue in this pool.
		"""
		# if we have a result of the search
		# check if any of our segments are in it
		for ele in self.elements:
			if ele.pool_search():
				ele.status = 'archived'
			else:
				ele.status = 'pending'
	
	def pool_search(self,element,refresh=False):
		"""
		Search for element.path in either the archive pool
		or the backup pool and return True if there is an exact match.

		TODO: search in the 'flame_archive' directory as well as 
		the 'flame_consolidate' directory.
		"""
		path = "%s/%s" % (self.catalog_path,element.filename)
		_pool = self._get_project_tina_entries(pool=element.pool,refresh=refresh)
		if _pool:
			for f in _pool._find(path=path):
#				print("    \x1b[48;5;28m\x1b[38;5;255mEntry found:%s\x1b[m" % (element.filename))
				# compare the dates
				# round the mod date to minutes
				file_date = element.mod_date.replace(second=0,microsecond=0)
				tina_date = TinaFind.convert_date(f['modification_date'])
				date_match = tina_date == file_date
#				print("    Tina date: %s" % tina_date)
#				if date_match:
#					print("    \x1b[38;5;82mFile date: %s\x1b[m" % file_date)
#				else:
#					print("    \x1b[38;5;196mFile date: %s\x1b[m" % file_date)

				# compare the file sizes
				target = "%s/%s" % (self.segment_path,element.filename)
				cnv_bytes = TinaFind.convert_bytes(f['size'],f['scale'])
				st_size = fileutil.st_size(target)
				size_match = Tina.compare_filesizes(cnv_bytes,st_size)
#				print("    Tina size: %s" % cnv_bytes)
#				if size_match:
#					print("    \x1b[38;5;82mFile size: %s\x1b[m" % st_size)
#				else:
#					print("    \x1b[38;5;196mFile size: %s\x1b[m" % st_size)

				if date_match and size_match:
#					print("    \x1b[48;5;28m\x1b[38;5;255mStatus: ARCHIVED\x1b[m")
					return True

				# if the size does not match for a header file,
				# and the pending file is actually smaller than 
				# the archived version we have a major problem.
				# This is the easiest place to step in and raise 
				# an important exception.
				if not size_match and element.element_type == 'header':
					if st_size < cnv_bytes:
						message = '\n\n[41mERROR[m: Current header is smaller than previously archived version'
						message += '\n  Path: %s' % target
						message += '\n    Filesize: %s' % st_size
						message += '\n    Archive size: %s\n\n' % cnv_bytes
						print message
						sys.exit()
		return False

	def _set_element_pools(self,search_old_apps=True):
		"""
		Set each elements 'pool' and 'state' based on the following:

		1. If base_dir is 'flame_backup' all elements go
		   to the backup pool.
		2. If base_dir is 'flame_archive' all elements go
		   to the archive pool.
		"""
		if self.base_dir == 'flame_archive':
			pool = 'archive'
		elif self.base_dir == 'flame_backup':
			pool = 'backup'
		elif self.base_dir == 'flame_consolidate':
			pool = 'archive'
		for hdr in self.headers:
			hdr.pool = pool
		for seg in self.segments:
			seg.pool = pool

	def generate_queue(self,pool):
		"""
		Return the the elements that 
		are eligible for the pool

		'pool' can be either:
			'backup' or 'archive
		"""
		queue = []
		for ele in self.elements:
			if ele.pool == pool and ele.status == 'pending':
				ele.abs_path = "/%s/%s/%s/%s" % (
					self.base_dir,
					self.parent_dir,
					self.project,
					ele.filename
					)
				queue.append(ele)
		return queue

	def _archive(self,pools=['backup','archive'],verbose=True,dry_run=False):
		"""
		Run the actual archive commands for 
		either or both pools
		"""
		if type(pools) is not list:
			pools = [pools]

		_start = datetime.today()
		self.archive_bytes = 0
		for pool in pools:
			queue = self.generate_queue(pool)
			log.info('%s: %s' % (pool.upper(),queue))
			if len(queue) == 0:
				message = "%s Warning: '%s' pool: Nothing to %s." % (pool.title(),pool,pool)
				log.info(message)
				if verbose:
					print "    %s" % message
				continue

			if verbose:
				print "\n  ++ %s POOL ++" % (pool.upper())
				print "    Creating %s of the following files:" % (pool)

			# create a filelist and calculate the size
			filelist = []
			for ele in queue:
				filelist.append(ele.abs_path)
				self.archive_bytes+=ele.st_size
				if verbose:
					print "      %s" % ele.abs_path
		
			# determine which strategy 
			# we're using
			if pool == 'archive':
				strat = 'A'
			elif pool == 'backup':
				strat = 'B'
			path = ' '.join(filelist)

####################### TESTING ###########################3
#			Tina.backup(path=path,application='fake_application',strat=strat,dry_run=dry_run)
####################### TESTING ###########################3
			Tina.backup(path=path,application='flame_archive',strat=strat,dry_run=dry_run)
		_stop = datetime.today()
		self.archive_delta = (_stop-_start)
		self.archive_seconds = (_stop-_start).seconds
		self.archive_size = numberutil.humanize(self.archive_bytes,scale='bytes')
		try:
			rph = (self.archive_bytes/self.archive_seconds)*3600
		except:
			rph = 0
		self.archive_rate = numberutil.humanize(rph,scale='bytes')


	@staticmethod
	def find_project_archived_name(
		project,
		search_old_apps=True,
		base_dir='flame_archive',
		skip_filter=None,
		application='flame_archive',
		full_search=False,
		verbose=False
	):
		"""
		Searches the top level directories in each application
		for occurences of 'project'. 

		Note: This method can be used to search for a project name.
		      e.g. '10A103' will return all directories that match 
			that pattern.
		"""
		results = {}
		year = Tina.parse_year(project)
		parent_dir = "/%s/%s" % (base_dir,year)

		# get the available parent directories
		# Note: If we try to search inside of 
		# a parent directory that does not exist,
		# tina_find will segfault
		existing_paths = []
		obj = Tina.tina_find(
			application=application,
			path_folder='/%s' % base_dir,
			list_all=False,
			recursive=False,
			skip_filter=skip_filter)
		for k,v in obj.data.iteritems():
			if base_dir in v['path']:
				existing_paths.append(v['path'])
		# if the year folder is an actual year, and it matches the
		# project's parsed year, then only search in that folder...
		# UNLESS the full_search flag is set
		if year != 'misc' and not full_search and parent_dir in existing_paths:
			path_folders = [parent_dir]
		else:
			path_folders = existing_paths

		for pfolder in path_folders:
			# skip directories that start with '.'
			if [x for x in pfolder.strip('/').split('/') if x[0] == '.']:
				continue
			if verbose:
				print "      \x1b[38;5;122mSearching in\x1b[m: %s" % (pfolder)
			obj = Tina.tina_find(
				application=application,
				path_folder=pfolder,
				list_all=False,
				recursive=False,
				skip_filter=skip_filter)
			if obj:
				for k,v in obj.data.iteritems():
					if project.lower() in v['path'].lower():
						#results.append(os.path.split(v['path'])[1])
						results[os.path.split(v['path'])[1]] = True
	
		if not search_old_apps:
			return results.keys()

		if application == 'flame_archive':
			for app,dirs in DiscreetArchive.OLD_APPS.iteritems():
				for top_lvl in dirs:
					obj = Tina.tina_find(
						application=app,
						path_folder=top_lvl,
						list_all=False,
						recursive=False,
						skip_filter=skip_filter)
					if obj:
						for k,v in obj.data.iteritems():
							if project.lower() in v['path'].lower():
								results[os.path.split(v['path'])[1]] = True
		return results.keys()

	def find_archived_project_files(self,
		search_old_apps=True,
		search_consolidate=False,
		search_backup=False):
		"""
		Search for a project in all the known
		applications and gather all of the 
		latest versions of the segments and headers.
		"""
		results = []
		if search_old_apps:
			results = self._search_old_applications(self.project)

		year = Tina.parse_year(self.project)
		# archive pool - strategy 'A'
#		if self.base_dir == 'flame_archive':
		if self.base_dir:
			#print "Searching flame_archive in archive pool"
			obj = self._get_project_tina_entries(pool='archive')
			if obj:
				results.append(obj)

			# if our base_path is 'flame_archive' we
			# need to search 'flame_consolidate' as well
			# NOTE: the reverse is NOT true. 
			#print "Searching flame_consolidate in archive pool"
			alt_path = "/flame_consolidate/%s" % ('/'.join(self.catalog_path.split('/')[2:]))
			obj = self._get_project_tina_entries(pool='archive',path_folder=alt_path,refresh=True)
			if obj:
				results.append(obj)

#		if self.base_dir == 'flame_backup':
#			#print "Searching flame_backup in backup pool"
#			# normally we shouldn't be restoring from flame_backup
#			# but it can happen
#			# backup pool - strategy 'B'
#			obj = self._get_project_tina_entries(pool='archive')
#			if obj:
#				results.append(obj)

		reduced = TinaFind.reduce_results(results)
		return reduced

	def _get_project_tina_entries(self,pool='archive',refresh=False,path_folder=None):
		"""
		Search the archive or backup pool for entries for this project.
		The search is persistent in the object and is stored 
		in the 2 attributes:
			self.tina_archive_entries
			self.tina_backup_entries
		If the search returns nothing then the value of these 
		attributes is None. If the attributes do not exist then
		the search has not been performed. This is important so certain
		calls will raise an exception if they attempt to do a comparison
		before the search is done.

		The object represents a project that exists in 
		"""
		if not path_folder: path_folder = self.catalog_path
		if not refresh:
			try:
				return self.tina_archive_entries
			except: pass  
		self.tina_archive_entries = Tina.tina_find(
			path_folder=path_folder,
			application=self.application,
			strat='A',
			skip_filter=self.skip_filter)
		return self.tina_archive_entries

#		NOTE: There is no longer a 'B' strategy - this should be removed eventually
#		if pool == 'archive':
#			# if we're searching the archive pool we want to search in
#			if not refresh:
#				try:
#					return self.tina_archive_entries
#				except: pass  
#			self.tina_archive_entries = Tina.tina_find(
#				path_folder=path_folder,
#				application=self.application,
#				strat='A',
#				skip_filter=self.skip_filter)
#			return self.tina_archive_entries
#		elif pool == 'backup':
#			if not refresh:
#				try:
#					return self.tina_backup_entries
#				except: pass
#			self.tina_backup_entries = Tina.tina_find(
#				path_folder=path_folder,
#				application=self.application,
#				strat='B',
#				skip_filter=self.skip_filter)
#			return self.tina_backup_entries
			
	def _search_old_applications(self,path,filename=None):
		"""
		Search for a filename in the older archive applications.
		Once the old applications are consolidated this search
		will not be necessary.
		"""
		# iterate through the applications and their top 
		# level directories and search for the given 'path'
		result_objs = []
		for app,dirs in self.OLD_APPS.iteritems():
			for top_lvl in dirs:
				path_folder = "%s/%s" % (top_lvl,path)
				if filename:
					obj = Tina.tina_find(
						application=app,
						path_folder=path_folder,
						pattern=filename,
						list_all=True,
						skip_filter=self.skip_filter)
				else:
					#print "Searching for:",app,path_folder
					obj = Tina.tina_find(
						application=app,
						path_folder=path_folder,
						list_all=True,
						skip_filter=self.skip_filter)
				if obj:
					result_objs.append(obj)
		return result_objs


class DiscreetArchiveElement:
	"""
	Class to represent either a segment or
	an element in a DiscreetArchive.
	"""

	def __init__(self,DA_obj,filename,state='unknown',pool='unknown',status='unknown',element_type='unknown'):
		"""
		da_obj is the DiscreetArchive object that is spawning
		this child class
		"""
		self.DA = DA_obj
		self.filename = filename
		self.target = "%s/%s" % (DA_obj.segment_path,filename)
		self.state = state
		self.pool = pool
		self.element_type = element_type
		self.mod_date = fileutil.mod_date(self.target)
		self.st_size = fileutil.st_size(self.target)

	def pool_search(self,**kwargs):
		"""
		Search for element.path in either the archive pool
		or the backup pool and return True if there is an exact match.
		"""
		return self.DA.pool_search(self,**kwargs)

	def validate_archive(self):
		"""
		Check all the files in the queue to see if 
		they made it to their respective pools.
		"""
		# refresh the archive pool searches
		self.pool_search(refresh=True)
		if self.status == 'archived':
			return True
		return False

class DiscreetConsolidate:
	"""
	Discreet archive tape consolidation class.

	Example tape id:
		Discreet_Archive0000707
	"""

	def __init__(	self,
				virtual_root=DiscreetArchive.VIRTUAL_ROOT,
				base_dir='flame_consolidate',
				application='flame_archive',
				dry_run=True):
		self.virtual_root = virtual_root
		self.base_dir = base_dir
		self.application = application
		self.dry_run = dry_run

		# full list of cartridges
		# in the catalog 
		# (will be populated later)
		self.tina_cartridges = []
		# default status for a cart
		self.cart_status='pending'
		self.restore_queue = {}
		self.excludes = self._set_excludes()

	
	def _set_excludes(self):
		"""
		NOTE: This has been fixed. The offending
		setup archive has been removed.

		Build a list of patterns we
		are going to exclude from
		the consolidation.

		This exists to skip (temporarily)
		the batch setups that got in the
		archive pool.
		"""

		# cartridges aren't actually excluded, rather
		# they are 'excluded' from the tina search 
		# since the tina searches take forever on these carts.
		# the file list for these carts comes from the db
		cart_exclude = [	
#					'Discreet_Archive0000020',
#					'Discreet_Archive0000023',
#					'Discreet_Archive0000024',
#					'Discreet_Archive0000026',
#					'Discreet_Archive0000029',
#					'Discreet_Archive0000036'
					]
		file_exclude = 	[
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/Para_CC_BFX01',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_FailPhone_split_BFX01',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_WilliamSplit_BFX01',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_failPhone_New_BFX01',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/.cheditor',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/Para_CC_BFX01.batch',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_FailPhone_split_BFX01.batch',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_WilliamSplit_BFX01.batch',
#					'/2009_archive/09A236_kgb_DA/09A236_KGB_2010_DA/para_failPhone_New_BFX01.batch',
#					'/2010_archive/10A103_Milky_Way_DA_NY/flame_settings_BU',
#					'/2010_archive/conformFS/p6/',
					]
		return {'cart_exclude':cart_exclude,'file_exclude':file_exclude}

	def __getattr__(self,name):
		message = "'%s' object has no attribute '%s'" % (__name__,name)
		raise AttributeError,message

	def __iter__(self,status='hold'):
		"""
		Iterate over the cartridges
		in numerical order
		"""
		for cart in sorted(self.get_cartridges(),key=lambda c: c.data['id_num']):
			yield cart

	def get_cartridges(self):
		"""
		Returns a list of 'pending' cartridges from the db
		turned into Cartridge objects.
		"""
		return Cartridge.find(pool_label='Discreet_Archive',status=self.cart_status)
	
	def _get_tina_cartridges(self):
		"""
		Get the full list of cartridges
		from the tina catalog
		"""
		tc = TinaCartControl()
		tc.get_pool()
		for k,v in tc.data.iteritems():
			obj = consolidation_pools.find(
				pool_label = v['pool_label'],
				name = v['name']
				)
			if not obj:
				obj = consolidation_pools(
					name=v['name'],
					pool_label=v['pool_label'],
					barcode=v['barcode']
				)
				obj._convert_tape_id()
				obj.save()
			else:
				obj[0]._convert_tape_id()
				obj[0].data['pool_label'] = v['pool_label']
				obj[0].save()
			self.tina_cartridges.append(Cartridge(**v))
		return self.tina_cartridges

	def create_restore_lists(self,path_dest):
		"""
		Each tina_restore command needs 2 files:
		-file_list <objects to restore>
		-file_list_dest <destination directories>
		Since there's a separate command for each
		application we need to include files
		only for a particular application
		"""
		lists = {}
		for obj in self.restore_queue['objects']:
			lists[obj.data['folder']] = {}

		for app in lists.keys():
			#print "Creating list for",app
			flist,dlist = self._create_restore_list(app,path_dest)
			lists[app]['filelist'] = flist
			lists[app]['destlist'] = dlist
		self.restore_queue['commands'] = lists
		
	def _create_restore_list(self,application,path_dest):
		"""
		Create a pair of lists for a particular
		application.
		"""
		filelist = '/tmp/dlc_%s_filelist.txt' % application
		destlist = '/tmp/dlc_%s_destlist.txt' % application
		fl = open(filelist,'w')
		dl = open(destlist,'w')
		for csf in self.restore_queue['objects']:
			if csf.data['folder'] == application:
				fl.write('%s\n' % csf.data['real_path'])
				dl.write('%s/%s\n' % (path_dest,csf.data['parent_dir']))
		fl.close()
		dl.close()
		self.restore_queue['filelist'] = filelist
		self.restore_queue['destlist'] = destlist
		return(filelist,destlist)
	
	def create_destination_dirs(self):
		"""
		For every csf object in the restore queue:
		1. form the destination directory
		2. store it in the csf object
		3. create the directory on the filesystem.
		"""
		for csf in self.restore_queue['objects']:
			year = Tina.parse_year(csf.data['project_directory'])
			csf.final_dest_dir = '%s/%s/%s/%s' % (	self.virtual_root,
										self.base_dir,
										year,
										csf.data['parent_dir'])
			csf.temp_restore_dir = '%s/.consolidate' % (csf.final_dest_dir)
			fileutil.makedirs(csf.final_dest_dir)

	def path_excluded(self,path):
		"""
		Check the path against our excludes list
		"""
		for pattern in self.excludes['file_exclude']:
			if pattern in path:
				#print "    [41mExcluding:[m",path
				return True
		return False

	def cart_excluded(self,cart):
		"""
		Check the cartridge against our excludes list
		"""
		for ex_cart in self.excludes['cart_exclude']:
			if cart == ex_cart:
				print "  [43mExcluding:[m %s (File list will be pulled from the database)" % (cart)
				return True
		return False

	def generate_restore_queue(self,cart_limit=5,find_latest=True):
		"""
		Generate a queue of restores up 
		to the 'cart_limit' number of tapes.

		This method excludes completed tapes
		and segments tracked in the db.
		"""
		cartridges = []
		restore_queue = []
		ttl_size = 0
		for cart in self:
			excluded_count = 0
			cart_status = cart.update_status()
			if cart_status != 'pending':
				print "  [33m%s[m: %-10s (cartridge has %s entries)" % (cart.data['name'],cart_status.upper(),cart_status)
				continue
			print "  Getting file list for: [44m%s[m" % (cart.data['name'])
			# if the cart is excluded, pull the file 
			# list from the db instead of tina
			# csf - consolidate file (model)
			cart_contents = cart.get_contents(object_type='file',db_only=self.cart_excluded(cart.data['name']))
			for csf in cart_contents:
				if csf.data['status'] == 'pending':
					# get the status of the file
					if self.path_excluded(csf.data['path']):
						excluded_count+=1
						csf.data['status'] = 'skip'
						csf.save()
					elif csf.consolidated():
						#print "CONSOLIDATED:",csf.data['uid'],csf.data['path']
						#print "  marking as 'duplicate' "
						csf.data['status'] = 'duplicate'
						csf.save()
					elif [x for x in restore_queue 
						if x.data['parent_dir'] == csf.data['parent_dir'] 
						and x.data['filename'] == csf.data['filename']]:
						# check to see if we have already added this file
						# to the queue. When processing a list often a file
						# will reoccur in the same list and the 'consolidated'
						# method only checks the db for processed entries.
						continue
					else:
						# the dry run lets us skip this stupidly slow tina call,
						# however we can't skip if we don't have real_tape_ids,
						# so if we don't have those, you are SOL and have to wait :)
						if find_latest or not csf.data['real_tape_ids']:
							try:
								latest = TinaFind.find_latest_archive_segment(csf.data['path'])
								csf.data['real_application'] = latest['application']
								csf.data['real_path'] = latest['path']
								csf.data['filesize'] = int(''.join([x for x in latest['size'] if x.isdigit()]))
								csf.data['scale'] = latest['scale']
								csf.data['mod_date'] = latest['modification_date']
								csf.data['real_tape_ids'] = latest['cartridges']
								csf.save()
							except TinaCompareError,message:
								print "      [41mDate Comparison Error[m"
								csf.data['status'] = 'compare_error'
								csf.data['error_desc'] = str(message)
								csf.data['real_tape_ids'] = []
								csf.save()
							except KeyboardInterrupt:
								raise
							except:
								csf.data['status'] = 'error'
								csf.data['error_desc'] = 'Could not find latest version of this file!'
								csf.data['real_tape_ids'] = []
								csf.save()

						# which cart for this entry are not already
						# in our cart queue?
						new_tape_ids = []
						for tape_id in csf.data['real_tape_ids']:
							if tape_id not in [c.data['name'] for c in cartridges]:
								new_tape_ids.append(tape_id)

						# if adding this entries tape_id's does not 
						# put us over the limit, add it...
						if (len(cartridges) + len(new_tape_ids)) <= int(cart_limit):
							for tape_id in new_tape_ids:
								try:
									obj = Cartridge.find(name=tape_id)[0]
								except:
									obj = Cartridge(name=tape_id)
									obj.save()
								cartridges.append(obj)
							# add this file to the restore queue and 
							# print the path
							restore_queue.append(csf)
							print "    ",csf.data['path']
							# add the filesize to the total
							_size = TinaFind.convert_bytes(csf.data['filesize'],csf.data['scale'])
							ttl_size += _size
						# ...if there was more than 1 tape_id to add above
						# then we may still be under the cart_limit
						elif len(cartridges) == int(cart_limit):
							# we only want to return when we have
							# exactly the cart_limit.
							self.restore_queue['cartridges'] = cartridges
							self.restore_queue['objects'] = restore_queue
							self.restore_queue['ttl_size'] = ttl_size
							return (cartridges,restore_queue)
			# update the cart status 
			# (in case it's status has changed)
			cart.update_status(verbose=False)

			if excluded_count > 0:
				print "    [41mWarning:[m %s files were excluded from %s" % (excluded_count,cart.data['name'])
			#break
		# at the end of the catalog we 
		# may not reach the cart_limit
		self.restore_queue['cartridges'] = cartridges
		self.restore_queue['objects'] = restore_queue 
		self.restore_queue['ttl_size'] = ttl_size
		return (cartridges,restore_queue)

	def _path_exclude(self,path):
		"""
		These exclusions have been fixed and are obsolete
		"""
		#exclusions = [	'10A103_Milky_Way_DA_NY/flame_settings_BU',
		#			'/2010_archive/conformFS/p6/0'
		#			]
		#for exc in exclusions:
		#	if exc in path:
		#		return True
		return False

	def check_cart_status(self,label):
		try:
			cart = Cartridge.find(name=label)[0]
		except:
			message = "Cartridge not found: %s" % label
			log.error(message)
			return
		for csf in cart.get_contents(object_type='file',db_only=self.cart_excluded(cart.data['name'])):
			print "-"*50
			path_folder = "/%s/%s" % (csf.data['archive_base_dir'],csf.data['parent_dir'])
			obj = Tina.tina_find(	path_folder=path_folder,
							pattern=csf.data['filename'],
							application='flame_archive',
							list_all=True)
							#strat=None)
			print obj.data
	
	
if __name__ == '__main__':
#	print DiscreetArchive.find_project_archived_name('10E198')
#	print DiscreetArchive.find_project_archived_name('12A108')
#	print DiscreetArchive.find_project_archived_name('toyota')
	print DiscreetArchive.find_project_archived_name('15A220')
#	print DiscreetArchive.find_project_archived_name('test')



#	DC = DiscreetConsolidate()
#	DC.check_cart_status('Discreet_Archive0000001')
#	DC.test_tina_find()
#	DC._get_tina_cartridges()
#	l = TinaFind.find_latest_archive_segment('/2009_archive/._09E150_adidas_asw_DA')

#	DA.archive('77A777_Project_01')
#	DA = DiscreetArchive('10A103_Milky_Way_DA')
##	DA.archive(close=True,dry_run=True)
#	for cart in Cartridge.find(name='Discreet_Archive0000002'):
#		for csf in cart.get_contents(object_type='file'):
#			print csf.data['status'],csf.data['path']

	"""
	erasing a tape:

	1. First try just erasing the tape:
		
		tina_cart_control -label blahblah -erase 

		If this works we are done.
		If that command fails, it means there are job_id's that span onto other tapes.
		We have to track down the job_id's and make sure we can lose them...
		so move on to step 2.


	2. find the job id's on a tape:

		tina_listcart -label Discreet_Archive0000001 -listjob
	
		returns:

		1054   appl.tina.a52.com.fs Backup A (Incr)            Data integrity  Complete   Mon Jan 25 19:02:19 2010   Mon Jan 25 22:31:30 2010  
		1019   appl.tina.a52.com.fs Backup A (Full)            Data integrity  Complete   Wed Jan 20 22:06:16 2010   Wed Jan 20 23:45:03 2010 



	3. Find all the files associated with all job_ids:

		tina_listjob -jobid 1054 -output_format csv -v_barcode -v_strat -v_path

		returns: 

	R00013;A;/2010_archive;
	R00013;A;/2010_archive/10A101_nescafe_ballonist_DA;
	R00013;A;/2010_archive/10A101_nescafe_ballonist_DA/10A101_nescafe_ballonist_DA;
	R00013;A;/2010_archive/10A101_nescafe_ballonist_DA/10A101_nescafe_ballonist_DA_1.seg;
	R00013;A;/2010_archive/10A103_Milky_Way_DA;
	R00013;A;/2010_archive/10A103_Milky_Way_DA/10A103_Milky_Way_DA;
	R00013;A;/2010_archive/10A103_Milky_Way_DA/10A103_Milky_Way_DA_1.seg;
	R00013;A;/2010_archive/10A103_Milky_Way_DA/10A103_Milky_Way_DA_2.seg;
	R00013;A;/2010_archive/10A104_03MH_ARMPIT_DA;
	R00013;A;/2010_archive/10A104_03MH_ARMPIT_DA/10A104_OSMH_ARMPIT_DA;
	R00013;A;/2010_archive/10A104_03MH_ARMPIT_DA/10A104_OSMH_ARMPIT_DA_1.seg;
	R00013;A;/2010_archive/10A105_NAVY_FLAG_DA;
	R00013;A;/2010_archive/10A105_NAVY_FLAG_DA/10A105_NAVY_FLAG_DA;
	R00013;A;/2010_archive/10A105_NAVY_FLAG_DA/10A105_NAVY_FLAG_DA_1.seg;
	R00013;A;/2010_archive/10A109_coke_snowball_DA;
	R00013;A;/2010_archive/10A109_coke_snowball_DA/10A109_coke_snowball_DA;
	R00013R00015;A;/2010_archive/10A109_coke_snowball_DA/10A109_coke_snowball_DA_1.seg;
	R00015;A;/2010_archive/10A109_coke_snowball_DA/10A109_coke_snowball_DA_2.seg;
	R00015;A;/2010_archive/10A212_QUALCOMM_DA;
	R00015;A;/2010_archive/10A212_QUALCOMM_DA/10A212_QUALCOMM_DA;
	R00015;A;/2010_archive/10A212_QUALCOMM_DA/10A212_QUALCOMM_DA_1.seg;
	R00015;A;/2010_archive/10E102_reliant_smokemac_DA;
	R00015;A;/2010_archive/10E102_reliant_smokemac_DA/10E102_reliant_smokemac_DA;
	R00015;A;/2010_archive/10E102_reliant_smokemac_DA/10E102_reliant_smokemac_DA_1.seg;



	4. Make sure every file in that list is expendable. Meaning every file has been consolidated.


	5. Run the erase with the -force option

		tina_cart_control -label blahblah -erase -force




	NOTE: to delete a single folder entry:
	tina_del -folder appl.tina.a52.com.fs -path_folder /10A103-Mil.... -r
	"""


	pass














