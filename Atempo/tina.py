

###############################################
#
#	Atempo wrapper
#
# A52 repo:
#
#   /net/doc/eng-stor/engineering/Engineering_2010/Software/Linux/Atempo/
#
# Sample commands:
#
#	tina_find -path_folder /2010_archive/09A195_Tabloid_DA/ -application tina.a52.com.fs\
#		-catalog_only -long -all -depth 10Y -identity root:XXXXXXX -display_cart
#
# 	tina_find -path_folder /2010_archive/09A195_Tabloid_DA/ -application tina.a52.com.fs\
#		-pattern "09A195_Tabloid_DA_1.seg" -catalog_only -long  -depth 10Y -identity root:XXXXXXX -event_to_console
#
# Environment:
#
#	source /usr/Atempo/tina/.tina.sh 
#
#
#
#
###############################################

import subprocess as subp
import os
import commands
import re
import sys
import datetime
import time
import traceback
from A52.utils import print_array
from A52.utils import numberutil
from A52.utils import stringutil
from A52.utils import fileutil
from A52.utils import dateutil
from models import catalog
from models import cartridges
from models import objects
from models import consolidation_pools
from models import consolidation_files
from models import job_ids
from models import cart_job_ids
from models import job_id_files
from A52.db import controller
db = controller()

import logging
# create a log for the this module
log = logging.getLogger('atempo_local')
try:
	log_handler = logging.handlers.RotatingFileHandler('/var/log/a52_atempo.log','a', 20000000, 10000)
except:
	log_handler = logging.handlers.RotatingFileHandler('/tmp/a52_atempo.log','a', 20000000, 10000)
log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
log_handler.setFormatter(log_format)
log.addHandler(log_handler)

# create a log for the tina events 
# basically all un-parseable lines 
# will go into this log
event = logging.getLogger('atempo_event')
try:
	event_handler = logging.handlers.RotatingFileHandler('/var/log/a52_atempo_event.log','a', 20000000, 10000)
except:
	event_handler = logging.handlers.RotatingFileHandler('/tmp/a52_atempo_event.log','a', 20000000, 10000)
event_format = logging.Formatter('%(message)s')
event_handler.setFormatter(event_format)
event.addHandler(event_handler)

#try:
#	import zipfile
#	COMPRESSION_SUPPORTED['zip'] = zipfile
#except ImportError:
#	pass

#class bzipRotatingFileHandler(logging.handlers.RotatingFileHandler):
#
#	
#	def __init__(self,*args,**kws):
#		compress_mode = kws.pop('compress_mode')
#		try:
#			self.compress_cls = COMPRESSION_SUPPORTED[compress_mode]
#		except KeyError:
#			raise ValueError('"%s" compression method not supported.' % compress_mode)
#
#		super(bzipRotatingFileHandler,self).__init__(self,*args,**kws)
#
#
#	def doRollover(self):
#		super(bzipRotatingFileHandler,self).doRollover()
#		
#		# compress the old log
#		old_log = self.baseFilename + ".1"
#		#with open(old_log) as log:
#		#	with self.compress_cls.open(old_log + '.gz','wb') as comp_log:
#		#		comp_log.writelines(log)
#		#os.remove(old_log)

#from IPython.Shell import IPShellEmbed
#ips = IPShellEmbed([''],banner = 'Dropping into IPython',exit_msg = 'Leaving Interpreter, back to program.')
#ips()


class TinaError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class TinaCatalogOrphanError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class TinaCompareError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class TinaUnknownCartridgeError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class TinaUnselectedRetentionTimeError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class TinaWriteProtectError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)

class InvalidDLArchivePathError(Exception):

	def __init__(self,message):
		self.message = message

	def __str__(self):
		return repr(self.message)



class Cartridge(consolidation_pools):
	"""
	Class to represent a cartridge
	in the tina catalog
	"""

	def __init__(self,**kwargs):
		self.args = kwargs
		self.convert_args(**kwargs)
		self._get_id_num()
		self.contents = []
	
	def __getattr__(self,name):
		if name == 'data':
			self.data = {}
			return self.data
		message = "'%s' object has no attribute '%s'" % (__name__,name)
		raise AttributeError,message

	def convert_args(self,**kwargs):
		"""
		Grab args that match fields 
		in the model.
		"""
		for k,v in kwargs.iteritems():
			if k in ['pool_label','name','barcode']:
				self.data[k] = v
	
	def _get_id_num(self):
		if self.data.has_key('name'):
			self.data['id_num'] = stringutil.extract_numbers(self.data['name'])

	def recycle(self):
		"""
		Check a cartridge to see if it is safe to recycle.
		Each file on a cartridge is checked to make sure 
		the latest version of the file exists in the 
		new consolidation pool
		"""
		# get the contents of the cartridge
		contents = self.get_contents(object_type='file')
		expendable = True
		for csf in contents:
			if not csf.expendable():
				#print "\tCannot delete: %s" % csf.data['path']
				expendable = False
				break

		if expendable:
			print "\n%s: [42mRecyclable[m\n" % self.data['name']
			self.data['recyclable'] = 1
			self.save()
		else:
			print "\n%s: [41mNOT Recyclable[m\n" % self.data['name']


	def update_status(self,verbose=False):
		"""
		Check the contents of a tape to determine it's status.

		The content list from tina_listcart is reconciled 
		against the db and the statuses are checked to 
		determine the status of the cartridge.

		NOTES:
		The status have a priority that determines the overall
		status of the cartridge. E.g. if there are any pending
		entries at all the overall status is 'pending' regardless
		of any other status on that cartridge. If there are no
		'pending' entries then the next status we look for is
		any kind of 'error' in which case the overall status 
		is determined as 'error'. Follow the comments below in
		the method to see the full priority.
		"""
		try:
			cfp_model = consolidation_pools.find(name=self.data['name'])[0]
		except:
			message = "Error: Tape not found in the db: %s" % self.data['name']
			raise Exception,message

		contents = consolidation_files.find(tape_id=self.data['name'])
		statuses = [c.data['status'] for c in contents]

		# pending           |
		# if any entry is 'pending' mark the 
		# cartridge as pending and return
		if 'pending' in statuses:
			msg = "cartridge still has pending entries"
			if verbose:
				print "%s: PENDING %s" % (self.data['name'],msg) 
			cfp_model.data['status'] = 'pending'
			cfp_model.save()
			return 'pending'

		# archive_error     |
		# compare_error     |
		# if any entry is 'error' mark the
		# cartridge as error and return
		for status in statuses:
			if 'error' in status:
				msg = "cartridge has 'error' entries"
				if verbose: 
					print "%s: ERROR %s" % (self.data['name'],msg) 
				# 'error' status is just makes us manually set it back to pending
				#cfp_model.data['status'] = 'error'
				#cfp_model.save()
				return 'error'

		# skip              |
		# if any entry is 'skip' mark the
		# cartridge as 'skip' and return
		if 'skip' in statuses:
			msg = "cartridge has 'skip' entries"
			if verbose:
				print "%s: SKIP %s" % (self.data['name'],msg) 
			#cfp_model.data['status'] = 'skip'
			#cfp_model.save()
			return 'skip'

		# invalid_path      |
		# if any entry is 'invalid_path' mark the
		# cartridge as 'invalid_path' and return
		if 'invalid_path' in statuses:
			msg = "cartridge has 'invalid_path' entries"
			if verbose:
				print "%s: INVALID_PATH %s" % (self.data['name'],msg) 
			#cfp_model.data['status'] = 'invalid_path'
			#cfp_model.save()
			return 'invalid_path'

		# restored          |
		# if any entry is 'restored' mark the
		# cartridge as 'restored' and return
		if 'restored' in statuses:
			msg = "cartridge has 'restored' entries"
			if verbose:
				print "%s: RESTORED %s" % (self.data['name'],msg) 
			#cfp_model.data['status'] = 'restored'
			#cfp_model.save()
			return 'restored'

		# archived          |
		# interceded        |
		# if any entry is either 'archived' or
		# 'interceded' mark the cartridge as 
		# 'archived' and return
		if 'archived' in statuses or 'interceded' in statuses:
			msg = "cartridge has 'archived' or 'interceded' entries"
			if verbose:
				print "%s: ARCHIVED %s" % (self.data['name'],msg) 
			cfp_model.data['status'] = 'archived'
			cfp_model.save()
			return 'archived'

		# duplicate_restore |
		# duplicate         |
		# directory         |
		# if we have not met any of the conditions above, we may have a
		# cartridge that is completely duplicates (or directories)
		for status in statuses:
			if 'duplicate' in status or 'directory' in status:
				msg = "cartridge has 'duplicate' or 'directory' entries"
				if verbose:
					print "%s: DUPLICATE %s" % (self.data['name'],msg) 
				#cfp_model.data['status'] = 'duplicate'
				#cfp_model.save()
				return 'duplicate'

	def get_contents(self,object_type=None,db_only=False):
		if db_only:
			return self._get_contents_db(object_type=object_type)
		else:
			return self._get_contents_tina(object_type=object_type)

	def _get_contents_db(self,object_type=None):
		"""
		Get the file listing of this cartridge
		from the db
		"""
		for obj in TinaObject.find(tape_id=self.data['name']):
			try:
				obj.data['real_tape_ids'] = eval(obj.data['real_tape_ids'])
			except:
				obj.data['real_tape_ids'] = []
			self.contents.append(obj)
		return self.contents

	def _get_contents_tina(self,object_type=None):
		"""
		Get the file listing of this cartridge
		from the tina command
		"""
		lc_obj = Tina.tina_listcart(self.data['name'])
		for k,v in lc_obj.data.iteritems():
			if not object_type or object_type == v['type']:
				try:
					obj = TinaObject.find(
						tape_id=self.data['name'],
						path=v['path'])[0]
				except:
					#traceback.print_exc()
					if v['type'] == 'dir':
						status = 'directory'
					elif v['type'] == 'file':
						status = 'pending'
					else:
						status = 'unknown'
					new_obj = TinaObject(
						tape_id=self.data['name'],
						folder=v['folder'],
						path=v['path'],
						object_type=v['type'],
						status=status
						)
					new_obj.save()
					# repull the record so we get all 
					# the fields as part of the object
					obj = TinaObject.find(uid=new_obj.data['uid'])[0]
				else:
					# update the object type if we didn't have one
					# set in the db already
					if not obj.data['object_type']:
						obj.data['object_type'] = v['type']
						if v['type'] == 'dir':
							obj.data['status'] = 'directory'
						elif v['type'] == 'file':
							obj.data['status'] = 'pending'
						else:
							obj.data['status'] = 'unknown'
						obj.save()
				try:
					obj.data['real_tape_ids'] = eval(obj.data['real_tape_ids'])
				except:
					obj.data['real_tape_ids'] = []

				self.contents.append(obj)
		return self.contents



class TinaObject(consolidation_files):
	"""
	Class to represent a tina 'object'
	which is basically a directory or
	file stored on a cartridge
	"""

	def __init__(self,**kwargs):
		self.data = kwargs
		self._split_path()
	
	def __getattr__(self,name):
		if name == 'data':
			self.data = {}
			return self.data
		message = "'%s' object has no attribute '%s'" % (__name__,name)
		raise AttributeError,message

	def parse_year(self):
		"""
		Figure out what year this archive
		is for by parsing the date that is
		'normally' at the beginning of the
		directory / filename.
		"""
		# try the filename first
		#regx = re.search('^([0-9]{2}[A-Z][0-9]{3})_.*',self.data['filename'])
		year = Tina.parse_year(self.data['filename'])
		if year:
			self.data['archive_base_dir'] = year
			self.save()
			return self.data['archive_base_dir']
		# last resort try the base_dir
		#regx = re.search('^([0-9]{2}[A-Z][0-9]{3})_.*',self.data['base_dir'])
		year = Tina.parse_year(self.data['base_path'])
		if year:
			#self.data['archive_base_dir'] = "20%s" % (regx.group(1)[:2])
			self.data['archive_base_dir'] = year
			self.save()
			return self.data['archive_base_dir']

		# can't determine the year
		# use 'misc' for anything we cannot parse
		self.data['archive_base_dir'] = "misc"
		self.save()
		return self.data['archive_base_dir']
	
	def _split_path(self):
		"""
		Split the path into 3 components;
		1. the top level directory, 
		2. the relative path 
		   (remaining directories
		   in the path)
		3. and the filename
		The first directory makes the 
		identity of the object ambiguous
		and must be separated for searches.
		"""
		if not self.data.has_key('path'):
			self.data['base_path'] = None
			self.data['parent_dir'] = None
			self.data['project_directory'] = None
			self.data['filename'] = None
			return

		if self.data['type'] == 'file':
			head,filename = os.path.split(self.data['path'])
			base_path,parent_dir = os.path.split(head)
		elif self.data['type'] == 'dir':
			filename = ''
			base_path,parent_dir = os.path.split(self.data['path'])

		self.data['base_path'] = base_path
		self.data['parent_dir'] = parent_dir
		self.data['project_directory'] = parent_dir
		self.data['filename'] = filename
		return

	def expendable(self):
		"""
		Check for this object in the 
		new archive and offsite archive pool
		to see if it's expendable.

		All files on a cartridge must be expendable
		in order for a cartridge to be recycled.
		"""
		# if we can't determine the archive_base_dir then exit
		if not self.data['archive_base_dir']:
			self.parse_year()

		print "\n\tChecking: %s/%s" % (self.data['path'],self.data['filename'])

		# find the latest version of this file
		latest = TinaFind.find_latest_archive_segment(self.data['path'])
		if not latest:
			print "\tCould not find latest version of this file."
			return False
		print "\t\tLatest found on cartridge(s): %s" % (' '.join(latest['cartridges']))

		# look for the latest version of the file in the new consolidation pool
		path_folder = "/flame_consolidate/%s/%s" % (self.data['archive_base_dir'],self.data['parent_dir'])
		tf = Tina.tina_find(
				path_folder=path_folder,
				application='flame_archive',
				pattern=self.data['filename'])
		if not tf:
			print "\t\t[41mError:[m File is not in the new archive pool"
			return False
		match = False
		for i,data in tf.data.iteritems():
			# compare this object against
			# what we found in the new pools:
			print "\t\tLatest : %10s %2s%28s" % (latest['size'],latest['scale'],latest['modification_date'])
			print "\t\tArchive: %10s %2s%28s" % (data['size'],data['scale'],data['modification_date'])
			log.info("Checking sizes: %s | %s" % (data['size'],latest['size']))
			if data['size'] != latest['size']:
				print "\t\t[41mSize mismatch:[m %s | %s" % (data['size'],latest['size'])
				continue
	
			log.info("Checking scale: %s | %s" % (data['scale'],latest['scale']))
			if data['scale'] != latest['scale']:
				print "\t\t[41mScale mismatch:[m %s | %s" % (data['scale'],latest['scale'])
				continue
	
			log.info("Checking dates: %s | %s" % (data['modification_date'],latest['modification_date']))
			if data['modification_date'] != latest['modification_date']:
				print "\t\t[41mDate mismatch:[m %s | %s" % (data['modification_date'],latest['modification_date'])
				continue
			match = True
			print "\t\t[42mMatch:[m Found on cartridge(s): %s" % (' '.join(data['cartridges']))
			break

		return match
	

	def validate_archive(self,virtual_root='/Volumes/F6412SATA01/flame_archive'):
		"""
		Validate the file with the entry
		in the new pool
		"""
		# file information
		target = "%s/%s/%s/%s" % (	virtual_root,
							self.data['archive_base_dir'],
							self.data['parent_dir'],
							self.data['filename'])
		file_size = fileutil.st_size(target)
		file_mod_date = fileutil.mod_date(target).replace(second=0,microsecond=0)
		#cmp_mod_date = mod_date.strftime("%Y%m%d%H%M")


		# find this file in the new pool
		path_folder = '/%s/%s' % (self.data['archive_base_dir'],self.data['parent_dir'])
		find = Tina.tina_find(path_folder=path_folder,pattern=self.data['filename'],application='flame_archive')
		# compare each entry found (should only be 1)
		# with the file info
		for i,info in find.data.iteritems():
			tina_size = TinaFind.convert_bytes(info['size'],info['scale'])
			tina_mod_date = TinaFind.convert_date(info['modification_date'])

		# compare the mod_dates
		if file_mod_date != tina_mod_date:
			message = "Modification date mismatch: tina(%s) real(%s)" % (tina_mod_date,file_mod_date)
			raise TinaError(message)

		# compare the file sizes
		if not Tina.compare_filesizes(tina_size,file_size):
			message = "File size discrepancy: tina(%s) real(%s)" % (tina_size,file_size)
			raise TinaError(message)

		# all good if we're here
		return True

	def validate_file_object(self,path_dest=''):
		"""
		Compare the object's modification date
		and filesize (approximately) to the 
		file on an array.

		*path_dest should be the entire absolute
	 	 path leading up to where the file is

		Note: the csv output of the tina_find command rounds
		      the object size and displays it in a more 
			'human' form. i.e. 211,956 KB
		"""
		target = "%s/%s" % (path_dest,self.data['filename'])
		# get the mod_date and the filesize 
		st_size = fileutil.st_size(target)
		mod_date = fileutil.mod_date(target)
		cmp_mod_date = mod_date.strftime("%Y%m%d%H%M")
		if type(self.data['mod_date']) is str:
			# convert the mod_date into a datetime
			self.data['mod_date'] = TinaFind.convert_date(self.data['mod_date'])
		cmp_date = self.data['mod_date'].strftime("%Y%m%d%H%M")

		# compare the mod_dates
		if cmp_mod_date != cmp_date:
			message = "Modification date mismatch: tina(%s) real(%s)" % (mod_date,self.data['mod_date'])
			raise TinaError(message)

		# compare the file sizes
		cnv_bytes = TinaFind.convert_bytes(self.data['filesize'],self.data['scale'])
		if not Tina.compare_filesizes(cnv_bytes,st_size):
			message = "File size discrepancy: tina(%s) real(%s)" % (cnv_bytes,st_size)
			raise TinaError(message)
		return True

	def search_application(self,application='flame_archive'):
		"""
		Check for this file in a tina application
		"""
		path_folder = "/%s/%s" % (self.data['archive_base_dir'],self.data['parent_dir'])
		obj = Tina.tina_find(path_folder=path_folder,pattern=self.data['filename'],application=application)
		if not obj:
			return False

		# check date and size
		for i,row in obj.data.iteritems():
			size = int(row['size'].replace(',',''))
			src_date = dateutil.legible_date(self.data['mod_date'],4)
			if 	size == self.data['filesize'] and\
				self.data['scale'] == row['scale'] and\
				src_date == row['modification_date']:
				return True
		return False


class TinaBase(object):


	def __init__(self):
		self.csv_split_count = 1
		self.command = "" 
		self.command_options = "" 
		self.data = {}
		self.count = 0
		self.db = False

	def source_env(self):
		env_file = '/usr/Atempo/TimeNavigator/tina/.tina.sh'
		newenvs = commands.getoutput("bash -c 'source %s; env'" % env_file)
		for line in newenvs.split('\n'):
			var = line[0:line.find('=')]
			value = line[line.find('=')+1:]
			os.environ[var] = value

	def run(self,parse=True,verbose=False):
		# form the command	
		self.form_command()
		log.info(self.command)
		if verbose:
			print " %s\n" % self.command
		# source the tina environment
		self.source_env()
		# run the find command
		self.status,self.output = self._exec(self.command)
		if self.status > 0:
			for line in self.output.split("\n"):
				event.info(line)
			raise TinaError,self.output
		if parse:
			# parse the output
			self._parse()

	def form_command(self):
		self.command = "%s %s -event_to_console" % (self.command," ".join(self.command_options))

	def _exec(self,command):
		#self._exec_start = datetime.datetime.today()
		self.status,self.output = commands.getstatusoutput(command)
		#self._exec_end = datetime.datetime.today()
		return self.status,self.output

		# NOTE: Popen returns the error codes from the shell directly
		# but was having some issues with random 'fdopen' errors.
		#proc = subp.Popen(command,shell=True,stdout=subp.PIPE,stderr=subp.PIPE)
		#status = proc.wait()
		#return (status,proc.stdout,proc.stderr)

	def _parse(self):
		"""
		Split the output from the command into a dictionary.
		"""
		log.info("Parsing output...")
		self._parse_start = datetime.datetime.today()
		data = {}
		if not self.output:
			message = "No results from search"
			raise TinaError,message

		split_lines = self.output.split('\n')
		i = 0
		for line in split_lines:
			if len(line.split(';')) == self.csv_split_count:
				data[i] = self._split_csv_line(line)
				i+=1
			elif line:
				# send any unparsed lines to the event log
				event.info(line)
		if not data:
			self.data = None
			self.count = 0
			#message = "No results from search"
			#raise TinaError,message
		else:
			# store the # of found entries
			self.count = len(data)
			self.data = data
		self._parse_end = datetime.datetime.today()
		log.info("Elapsed: %s" % (self._parse_end-self._parse_start))

	def _split_csv_line(self,line):
		split = line.split(';')
		info = {}
		for i in range(0,len(self.columns),1):
			info[self.columns[i]] = split[i]
		return info

	@staticmethod
	def convert_cartridges(cart_str):
		"""
		Convert the cartridge output
		from tina into a python list.
		"""
		return re.findall('[A-Za-z_]*[0-9]{7}',cart_str)
				
class TinaODBFree(TinaBase):
	"""
	tina_odbfree -jobid 1057 
	"""
	
	def __init__(self):
		self.data = {}
		self.db = False
		self.command = "tina_odbfree"

	def delete_job(self,job_id):
		"""
		Delete a job id from the tina catalog permanently
		"""
		self.command_options = [
			'-jobid %s' % (job_id)
			]
		try:
			record = job_ids.find(job_id=job_id)[0]
		except:
			message = 'JOB: Job ID: %s not found in db' % job_id
			raise Exception,message
		# run the actual delete
		self.run(parse=False)
		record.data['status'] = 'deleted'
		record.save()
		

class TinaLibraryControl(TinaBase):
	"""
	tina_library_control -reinit_barcode -library library_01  -event_to_console
	tina_library_control -online -library library_01  -event_to_console
	tina_library_control -content -library library_01  -event_to_console -short
	tina_library_control -list -library library_01  -event_to_console
	"""
	
	def __init__(self):
		self.data = {}
		self.db = False
		self.command = "tina_library_control"

	def offline_cart(self,barcode):
		"""
		Move a cart from the library into the 'mailbox'

		# success message:
		#"Cartridge "Discreet_Archive0000007" offline"
		"""
		self.command_options = [
			'-library library_01',
			'-barcode %s' % (barcode),
			'-offline'
			]
		self.run(parse=False)
		


class TinaRestore(TinaBase):

	# tina_restore -path_folder "/2010_archive/10A105_NAVY_FLAG_DA" -folder appl.tina.a52.com.fs -path_dest /Volumes/F5412SATA03/kb_restore_test/ -depth 10Y
	
	def __init__(self,	path_folder=None,
					application='appl.tina.a52.com.fs',
					path_dest='/Volumes/F6412SATA01/consolidation',
					file_list=None,
					dest_list=None,
					mode='abort',
					depth='10Y',
					strat=None):
		self.command = "tina_restore"
		try:
			self.application = Tina.APPLICATIONS[application]
		except:
			self.application = application
		self.depth = depth
		self.path_folder = path_folder
		self.path_dest = path_dest
		self.file_list = file_list
		self.dest_list = dest_list
		self.mode = mode
		self.strat = strat
		self.command_options = [
			"-folder %s" % self.application,
			"-depth %s" % self.depth,
			"-mode %s" % self.mode
			]
		if self.strat:
			self.command_options.append("-strat %s" % self.strat)
		if self.file_list and self.dest_list:
			self.command_options.append("-file_list %s" % self.file_list)
			self.command_options.append("-file_list_dest %s" % self.dest_list)
		else:
			self.command_options.append("-path_dest %s" % self.path_dest)
			self.command_options.append("-path_folder %s" % self.path_folder)
		self.data = {}
		self.db = False


class TinaBackup(TinaBase):

	"""
	Usage: tina_backup  	-strat A|B|C|D [-full]|[-incr] [-host host]|[-application application]
					[-date yyyymmddhhmm] [-path path]|[-file_list file_path]|
					[-parallel_file_list file_path] [-user user] [-password password] 
					[-encode] [-compress] [-sync_cart] [-v_jobid] [-identity identity] 
					[-catalog catalog] [-help] 

	Allows to run backups and to back up objects. 

	where options include:
		-strat A|B|C|D                     Specifies the backup strategy to use
		-full                              Starts a full backup. This is the default value.
		-incr                              Starts an incremental backup.
		-host host                         Specifies the host onto which the backup is initiated 
								(if not specified, the backup is started on local machine)
		-application application           Specifies the application onto which the backup is initiated
		-date yyyymmddhhmm                 Specifies the backup date
		-path path                         Specifies absolute paths of objects to be backed up
		                                    alias on this option is:  -path_src
		-file_list file_path               Specifies the path of a file containing the absolute paths 
								of objects to be archived (the paths must be separated by 
								carriage returns).
		-user user                         Specifies the name of the user performing the backup
		-password password                 Specifies the user password 
		                                     Can be used only if option  "-user" is used
		-encode                            Specifies that backed up data must be encrypted
		-compress                          Specifies that backed up data must be compressed 
		-sync_cart                         Specifies that the backup is considered as completed 
								once data has actually been written on cartridges. 
								If not specified, the backup is complete once data 
								has been written in the cache.
		-parallel_file_list file_path      Specifies absolute paths of files containing absolute 
								paths of files to be backed up. Each list of files will 
								be backed up simultaneously
		-v_jobid                           Specifies to display the job id
		-identity identity                 Catalog identity of the user. Identity format is "user:passwd" 
								or "user"
		-catalog catalog                   Catalog name
		-help                              This page
		                                     alias on this option is:  -h


		#TESTING NOTES:
		You have filesystem application Discreet_2010 with virtual root of /Volumes/F6412SATA01
		You have a backup selection of /hoop_test which applies to both strategy b & c
		Strategy B is backup strategy which goes to dl_backup_test pool in tar format
		Strategy C is Archive strategy which goes to dl_archive_test pool in tar format.

		tina_backup -full -strat C -application Discreet_2010_Archive -path /<segment_file>
		tina_backup -full -strat C -application Discreet_2010_Archive -path /hoop_test/2012_archive/dl_archive_6.seg /hoop_test/2012_archive/dl_archive_8.seg
	"""

	
	def __init__(self,path,strat='A',application=None,full=True):
		self.command = "tina_backup"
		self.path = path
		self.strat = strat
		self.application = application
		self.command_options = [
			"-strat %s" % self.strat,
			"-application %s" % self.application,
			]
		if type(self.path) is list:
			self.command_options.append("-path %s" % (" ".join(self.path)))
		else:
			self.command_options.append("-path %s" % self.path)
		if full:
			self.command_options.append("-full")
		else:
			self.command_options.append("-incr")
		self.data = {}


class TinaFind(TinaBase):

	# find statuses:
	FOUND_SET_NONE = 0x01
	FOUND_SET_EMPTY = 0x02
	FOUND_SET_MATCH = 0x03
	FOUND_SET_ERROR = 0x04

	def __init__(self,path_folder,pattern=None,application='tina.a52.com.fs',depth='10Y',list_all=False,recursive=True,strat=None):
		#print "PATH FOLDER:",path_folder
		self.application = application
		self.path_folder = path_folder
		self.pattern = pattern
		self.depth = depth
		self.list_all = list_all
		self.recursive = recursive
		self.strat = strat
		self.command = "tina_find"
		self.command_options = [
			"-output_format csv",
			"-long",
			"-catalog_only",
			"-display_cart",
			"-application %s" % application,
			"-depth %s" % depth,
			"-path_folder %s" % path_folder
			]
		#	"-event_to_console", # leaving this out for now
		if pattern:
			self.command_options.append("-pattern '%s'" % pattern)
		if list_all:
			self.command_options.append("-all")
		if not recursive:
			self.command_options.append("-no_r")
		if strat in ['A','B','C','D']:
			self.command_options.append("-strat %s" % strat)
		self.data = {}
		self.count = 0
		self.db = False
		self.csv_split_count = 12
		# the state of the found set (default is none)
		self.found_status = TinaFind.FOUND_SET_NONE
		# store the size of the found set in bytes
		# and the human readable form
		self.found_size = 0
		self.found_size_human = ''

	def run(self,**kwargs):
		"""
		Wrapper for the TinaBase.run.
		"""
		try:
			super(TinaFind,self).run(kwargs)
		except:	
			self.found_status = TinaFind.FOUND_SET_ERROR

		# set the status of the find
		if self.data == {} or self.data == None:
			self.found_status = TinaFind.FOUND_SET_EMPTY
		elif len(self.data) > 0:
			self.found_status = TinaFind.FOUND_SET_MATCH

	def found_status(self):
		"""
		Return the status of the current find
		"""
		return self.found_status

	def _find(self,**kwargs):
		"""
		Return a subset of the 
		current search output based
		on the kwargs.
		"""
		found_set = []
		for k,v in kwargs.iteritems():
			for i,data in self.data.iteritems():
				try:
					if v == data[k]:
						found_set.append(data)
				except:
					traceback.print_exc()
					pass
		return found_set
	
	def find_size(self):
		"""
		Find the total size of the current 
		find data (self.data)

		Scales reported by tina (so far):
		'KB', 'Bytes', 'MB'
		"""
		sizes = {}
		for i,d in self.data.iteritems():
			size = int(''.join([x for x in d['size'] if x.isdigit()]))
			if size > 0:
				try:
					sizes[d['scale']] += size
				except:
					sizes[d['scale']] = size

		total = 0
		for scale,size in sizes.iteritems():
			if scale == 'MB':
				total += size*1024*1024
			elif scale == 'KB':
				total += size*1024
			elif scale == 'Bytes':
				total += size
		self.found_size = total
		self.found_size_human = numberutil.humanize(total,scale='bytes')

	def newest(self):
		"""
		Find the newest object in the found set (latest date).
		Returns the object with the latest modified date, and 
		the object with the latest backup date.
		"""
		max_mod_obj = None
		max_bak_obj = None
		max_mod_date = None
		max_bak_date = None
		for k,v in self.data.iteritems():
			obj_mod_date = TinaFind.convert_date(v['modification_date'])
			obj_bak_date = TinaFind.convert_date(v['backup_date'])
			if not max_mod_date or obj_mod_date > max_mod_date:
				max_mod_date = obj_mod_date
				max_mod_obj = v
			if not max_bak_date or obj_bak_date > max_bak_date:
				max_bak_date = obj_bak_date
				max_bak_obj = v
		return (max_mod_obj,max_bak_obj)

	def get_cartridges(self):
		"""
		Get a list of cartridges 
		from self.data (the result
		of the find). 
		NOTE: Duplicates are only
			listed once in the return
		"""
		labels = {}
		for i,info in self.data.iteritems():
			_list = info['cartridges'].strip().split(',')
			for label in _list:
				labels[label.strip('[').strip(']')] = True
		return labels.keys()
				
	def create_db_entries(self):
		print "Creating entries..."
		if self.db:
			self._db_start = datetime.datetime.today()
			for id,entry in self.data.iteritems():
				c = catalog(**entry)
				c.blind_create()
				#c.save()
			self._db_end = datetime.datetime.today()
			print "Elapsed:",self._db_end-self._db_start

	def _split_csv_line(self,line):
		#file;182020;100;6,473;MB;2011-08-02 22:05;2011-08-03 02:12;;;;/2010_archive/11A168_Best_Buy_Trade_In_DA/11A168_Best_Buy_Trade_In_DA_6.seg; [Discreet_Archive0000572]
		split = line.split(';')
		object_type = split[0]
		path = split[10]
		base_path,parent_dir,filename = ['','','']
		# split the path based on the following format:
		# base_dir/relative_path/filename
		if object_type == 'file':
			head,filename = os.path.split(path)
			base_path,parent_dir = os.path.split(head)
		elif object_type == 'dir':
			base_path,parent_dir = os.path.split(path)

#		filename = split[10].lstrip('/').split('/')
#		if len(filename) > 0:
#			base_dir = filename[0]
#		if len(filename) > 1:
#			parent_dir = filename[1]
#		if len(filename) > 2:
#			relative_path = "/".join(filename[2:])

		return {	'type':object_type,
				'user_id':split[1],
				'group_id':split[2],
				'size':split[3],
				'scale':split[4],
				'modification_date':split[5],
				'backup_date':split[6],
				'unknown_a':split[7],
				'unknown_b':split[8],
				'offline':split[9],
				'path':split[10],
				'base_path':base_path,
				'parent_dir':parent_dir,
				'filename':filename,
				'cartridges':TinaBase.convert_cartridges(split[11]),
				'application':self.application,
				'strategy':self.strat}

	@staticmethod
	def reduce_results(objs):
		"""
		Reduce a found set by removing
		duplicates, incrementals etc. and
		returning only the latest version of each file.
		Other TinaFind objects can be passed in and added
		to the found set.
		"""
		_set = []
		reduced_set = {}
		if not type(objs) is list:
			objs = [objs]
		# gather all the objects' data
		for obj in objs:
			for i,info in obj.data.iteritems():
				_set.append(info)
		for info in _set:
			primary_key = "/%s/%s" % (info['parent_dir'],info['filename'])
			if reduced_set.has_key(primary_key):
				reduced_set[primary_key] = TinaFind.compare(reduced_set[primary_key],info)
			else:
				reduced_set[primary_key] = info
		return reduced_set

	@staticmethod
	def compare(a,b):
		"""
		Compare 2 found results
		and return the most current
		result.

		The latest version of the file 
		is determined by both the modified
		date and the backup date being greater.
		"""
		# compare file names
		a_name = "%s/%s" % (a['parent_dir'],a['filename'])
		b_name = "%s/%s" % (b['parent_dir'],b['filename'])
		log.info("Comparing:")
		log.info("-"*70)
		log.info("  A PATH: %s" % a['path'])
		log.info("  B PATH: %s" % b['path'])
		log.info("  A APP: %s" % a['application'])
		log.info("  B APP: %s" % b['application'])
		if a_name != b_name:
			message = "File names do not match"
			raise Exception,message

		# DATE MODIFIED
		a_mod_date = TinaFind.convert_date(a['modification_date'])
		b_mod_date = TinaFind.convert_date(b['modification_date'])
		log.info("    MOD A: %s" % a_mod_date)
		log.info("    MOD B: %s" % b_mod_date)
		if b_mod_date == a_mod_date:
			latest_mdate = '='
		elif b_mod_date > a_mod_date:
			latest_mdate = b
			log.info("      GREATER (B): %s" % b_mod_date)
		else:
			latest_mdate = a
			log.info("      GREATER (A): %s" % a_mod_date)

		# BACKUP DATE
		a_bkp_date = TinaFind.convert_date(a['backup_date'])
		b_bkp_date = TinaFind.convert_date(b['backup_date'])
		log.info("    BKP A: %s" % a_bkp_date)
		log.info("    BKP B: %s" % b_bkp_date)
		if a_bkp_date == b_bkp_date:
			latest_bdate = '='
		elif b_bkp_date > a_bkp_date:
			latest_bdate = b
			log.info("      GREATER (B): %s" % b_bkp_date)
		else:
			latest_bdate = a
			log.info("      GREATER (A): %s" % b_bkp_date)

#		# POOL
#		# Defer to the 'flame_archive' pool if 'a' 
#		# or 'b' are part of it. (harmless if not)
#		log.info("    POOL A: %s" % a['application'])
#		log.info("    POOL B: %s" % b['application'])
#		if a['application'] == b['application'] == 'flame_archive':
#			if a['strategy'] == 'A' != b['strategy']:
#				latest_pool = a
#			elif b['strategy'] == 'A':
#				latest_pool = b
#			else:
#				latest_pool = a
#		elif a['application'] == 'flame_archive':
#			latest_pool = a
#		elif b['application'] == 'flame_archive':
#			latest_pool = b
#		else:
#			latest_pool = a

		# If everything is equal:
		if latest_mdate == '=':
#			if latest_bdate == '=':
#				# if both dates were the 
#				# same default to the 
#				# latest_pool
#				latest_bdate = latest_pool
			latest_mdate = latest_bdate

		# if the latest mod date object is
		# the same as the latest backup date
		# object then return that object.
		if latest_mdate == latest_bdate:
			if latest_mdate == a:
				log.info("      RETURN: A")
			else:
				log.info("      RETURN: B")
			return latest_mdate
		else:
			print "\n Date comparison could not be reconciled: %s \n" % (a_name)
			print "  Modified date:"
			print "    A: %s" % (a_mod_date)
			print "    B: %s" % (b_mod_date)
			print "  Backup date:"
			print "    A: %s" % (a_bkp_date)
			print "    B  %s\n" % (b_bkp_date)
			dates = [	(a_mod_date,'\x1b[38;5;081mA:MOD\x1b[m','\x1b[38;5;081m%s\x1b[m' % a_mod_date),
					(b_mod_date,'\x1b[38;5;208mB:MOD\x1b[m','\x1b[38;5;208m%s\x1b[m' % b_mod_date),
					(a_bkp_date,'\x1b[38;5;081mA:BKP\x1b[m','\x1b[38;5;081m%s\x1b[m' % a_bkp_date),
					(b_bkp_date,'\x1b[38;5;208mB:BKP\x1b[m','\x1b[38;5;208m%s\x1b[m' % b_bkp_date)]
			print "  Timeline view:"
			print "     %-36s%-36s%-36s%-36s" % tuple(["       %s ->" % y[1] for y in sorted(dates,key=lambda x: x[0])])
			print "     %s%s%s%s" % tuple(["%-36s" % y[2] for y in sorted(dates,key=lambda x: x[0])])
			print "\n"
			message = "Date comparison could not be reconciled: %s " % (a_name)
			message+= "A:[MOD:%s] [BKP:%s] B:[MOD:%s] [BKP:%s]" % (a_mod_date,a_bkp_date,b_mod_date,b_bkp_date)
			raise TinaCompareError,message

	@staticmethod
	def convert_bytes(size,scale):
		"""
		Convert a the size and scale
		combination from the return 
		of the tina_find 'csv' mode 
		into bytes.
		"""
		try:
			size = int(size.replace(',',''))
		except:pass
		if scale == 'Bytes':
			return size
		if scale == 'KB':
			return size*1024
		if scale == 'MB':
			return size*1024*1024
		if scale == 'GB':
			return size*1024*1024*1024
		message = "Unknown scale factor: %s" % scale
		raise Exception,message

	@staticmethod
	def convert_date(date):
		"""
		Convert a date string returned
		from a tina_find command into
		a datetime object
		Example:
		2011-07-14 02:50
		"""
		return datetime.datetime(*[int(c) for c in re.findall('\d+',date)])

	@staticmethod
	def find_latest_archive_segment(path,list_all=True):
		"""
		Search the tina applications for occurrences
		of the given segment and return the latest
		version.

		There are 3 applications to search through
		each having 1 or more top level directories.

		latest = TinaFind.find_latest_archive_segment('/2010_archive/File___/mnt/nas3/2010_archive')

		"""
		split = path.split('/')
		if len(split) <= 3:
			message = "Path is too short: %s" % path
			raise InvalidDLArchivePathError,message

		applications = {	'tina.a52.com.fs':['/2007_archive','/2008_archive','/2009_archive','/2010_archive','/archive'],
					'Discreet_2010_Archive':['/2010_archive'],
					'Discreet_2011_Archive':['/2011_archive'],
					}
		# remove any occurrence of the top level directories
		# since they are added automatically in the searches
		for app,dirs in applications.iteritems():
			for top_lvl in dirs:
				#if re.search(top_lvl,path):
				if top_lvl.strip('/') == split[1]:
					path = "/%s" % ( "/".join(split[2:]))
					split = path.split('/')
					break

		# iterate through the applications and their top 
		# level directories and search for the given 'path'
		result_objs = []
		for app,dirs in applications.iteritems():
			for top_lvl in dirs:
				path_folder = "%s/%s" % (top_lvl,"/".join(split[:-1]).strip('/'))
				segment = split[-1]
				#print "Searching for %s/%s in %s" % (path_folder,segment,app)
				#print "Tina.tina_find(application=",app,",path_folder=",path_folder,",pattern=",segment,",list_all=True)"
				obj = Tina.tina_find(application=app,path_folder=path_folder,pattern=segment,list_all=list_all)
				if obj:
					if obj.data:
						result_objs.append(obj)

		# the find object can contain multiple results... reduce 
		# them here and return the reduced result
		if result_objs:
			# since we're only feeding the reduction routine one 
			# path the result is going to be only one entry so
			# just return in the first iter...
			for k,v in TinaFind.reduce_results(result_objs).iteritems(): 
				return v
		else:
			message = "No reference found in any application (orphaned file): %s" % path
			raise TinaCatalogOrphanError,message
		return None


class TinaListJob(TinaBase):
	"""
	tina_listjob -jobid 1054 -output_format csv -v_barcode -v_strat -v_path

	Displays the list of all objects attached to a given job 

	where options include:
		-jobid jobid                                   Specifies the ID of the job to which the list of objects to display is attached
		-force                                         Specifies that the list of objects must be displayed even if jobs are running (resources used may slow down running jobs)
		-max_obj max_obj                               Specifies the maximum number of objects retrieved by a request
		-all                                           Specifies that all objects processed in all sessions of specified job are displayed
		-output_format Format                          Specifies the format used to display the data. Values can be: text or csv
		-csv_separator separator                       Specifies the separator used with the CSV format (default value is ";")
		                                                 Can be used only if option  "-output_format" is used
		-v_size                                        Displays object size
		-volume_unit Unit                              Specifies the unit used to display file size. Values can be byte, kilo, mega, giga, tera or best (default value is "byte")
		-v_path                                        Displays object names 
		-v_type                                        Displays object type 
		-v_backup_date                                 Displays the object backup dates 
		-v_last_access_date                            Displays objects last access date 
		-v_modification_date                           Displays objects last modification date 
		-v_info_cart                                   Displays cartridge information on objects 
		-v_barcode                                     Displays the cartridge barcodes of the objects
		-v_host                                        Displays object host 
		-v_strat                                       Displays object strategy
		-v_sess                                        Displays object session
		-v_default                                     Displays default columns (-v_info_cart, -v_type, -v_backup_date, -v_size, -v_path)
		-catalog catalog                               Catalog name

	"""

	def __init__(self,job_id):
		self.job_id = job_id
		self.data = {}
		self.command = "tina_listjob"
		self.command_options = [
			"-jobid %s" % job_id,
			"-output_format csv",
			"-force",
			"-v_info_cart",
			"-v_barcode",
			"-v_path",
			"-v_type",
			"-v_strat",
			"-v_backup_date",
			"-v_modification_date"
			]
		self.columns = [
			'cart_info',
			'barcode',
			'path',
			'type',
			'strategy',
			'backup_date',
			'modification_date'
			]
		self.csv_split_count=8
	
	def parse_cart_info(self):
		"""
		Get the tape name out of the cart info and 
		store it in the data dict (for the db)
		"""
		for k,v in self.data.iteritems():
			v['tape_name'] = v['cart_info'].split('(')[0]


class TinaListCart(TinaBase):
	"""
	tina_listcart -label Discreet_Archive0000663 -v_type -v_path -v_backup_date -v_modification_date -v_info_cart -v_folder -output_format csv

	tina_listcart -label Discreet_Archive0000001 -listjob -output_format csv

	1054;appl.tina.a52.com.fs;Backup A (Incr);Data integrity;Complete;2010-01-25 19:02;2010-01-25 22:31;
	1019;appl.tina.a52.com.fs;Backup A (Full);Data integrity;Complete;2010-01-20 22:06;2010-01-20 23:45;
	"""

	def __init__(self,label,job_ids=False):
		self.label = label
		self.data = {}
		self.db = False
		self.command = "tina_listcart"

		if job_ids:
			self.command_options = [
				"-output_format csv",
				"-label %s" % self.label,
				'-listjob'
				]
			self.columns = [
				'job_id',
				'filesystem',
				'strategy',
				'data_integrity',
				'status',
				'backup_date',
				'modification_date'
				]
			self.csv_split_count=8
		else:
			self.command_options = [
				"-output_format csv",
				"-label %s" % self.label,
				'-v_info_cart',
				'-v_type',
				'-v_path',
				'-v_backup_date',
				'-v_modification_date',
				'-v_folder'
				]
			self.columns = [
				'tape_file',
				'tape_offset',
				'size',
				'type',
				'path',
				'backup_date',
				'modification_date',
				'folder'
				]
			self.csv_split_count=9

	def create_db_entries(self):
		if not self.db:
			print "DB not set"
			return
		print "Creating entries..."
		self._db_start = datetime.datetime.today()
		for id,entry in self.data.iteritems():
			c = objects(**entry)
			c.data['cart_name'] = self.label
			c.blind_create()
		self._db_end = datetime.datetime.today()
		print "Elapsed:",self._db_end-self._db_start


class TinaCartControl(TinaBase):
	"""
	tina_cart_control -pool Discreet_Archive -list

	To make things easier I'm only going to support -output_format csv
	CSV:
	Discreet_Archive0000661;R01148;1785;GB;Partly filled;drive_02;No (data integrity);;Open;Partly filled;
	Discreet_Archive0000655;R01140;191574;MB;Closed on error;library_01;No (data integrity);;Closed on error;Partly filled;
	Discreet_Archive0000656;R01141;1762;GB;Full;library_01;No (data integrity);;Closed;Full;
	CSV (long):
	Discreet_Archive0000662;R01150;193024;Bytes;1;Partly filled;2011-10-17 18:27;drive_02;;;2011-10-17 18:27;;tar;0.00;No (data integrity);;HP Ultrium 5;Discreet_Archive;Open;Partly filled;
	Discreet_Archive0000655;R01140;191574;MB;2;Closed on error;2011-10-07 23:22;library_01;;;2011-10-07 23:22;2011-10-10 13:11;tar;0.00;No (data integrity);;HP Ultrium 5;Discreet_Archive;Closed on error;Partly filled;
	Discreet_Archive0000656;R01141;1762;GB;1;Full;2011-10-10 16:05;library_01;;;2011-10-10 16:05;2011-10-10 13:11;tar;0.00;No (data integrity);;HP Ultrium 5;Discreet_Archive;Closed;Full;
	"""


	def __init__(self):
		self.data = {}
		self.db = False
		self.command = "tina_cart_control"

	def get_label_info(self,label):
		"""
		Translate the 'label' to a barcode
		and grab the location status.
		"""
		self.command_options = [
			'-label %s' % (label),
			'-status',
			'-v_barcode',
			'-v_location',
			'-output_format csv',
			]
		self.columns = [
			'barcode',
			'location',
			]
		self.csv_split_count=3
		self.run()
		# the header line is at index 0
		# which we don't care about so return
		# the info line wich is at 1
		self.data = self.data[1]

	def erase_cart(self,label,force=False):
		"""
		Erase a cartridge. This command will
		remove the header from the tape permanently
		removing it from the catalog.
		"""
		self.command_options = [
			'-label %s' % (label),
			'-erase',
			]
		try:
			record = consolidation_pools.find(name=label)[0]
		except:
			message = 'Cart: %s not found in db' % label
			raise Exception,message

		if force:
			self.command_options.append('-force')
		try:
			self.run(parse=False)
		except:
			for line in self.output.split('\n'):
				if "is write protected" in line:
					message = "ERROR: %s is write protected."
					raise TinaWriteProtectError,message
			raise
		else:
			for line in self.output.split('\n'):
				if "is in retention time: Unselected" in line:
					message = "ERROR: Obscure tina error: '%s is in retention time: Unselected' "
					raise TinaUnselectedRetentionTimeError,message
				if line == "Cartridge operation is done":
					record.data['status'] = 'erased'
					record.save()
					return

	def get_pool(self,pool='Discreet_Archive'):
		self.pool = pool
		self.command_options = [
			'-pool %s' % self.pool,
			'-list',
			'-output_format csv',
			'-v_name',
			'-v_barcode',
			'-v_volume',
			'-v_unit',
			'-v_tape_file',
			'-v_status',
			'-v_recycling',
			'-v_location',
			'-v_rule',
			'-v_description',
			'-v_creation_date',
			'-v_backup_date',
			'-v_format',
			'-v_wear_level',
			'-v_recyclable',
			'-v_recycle_age',
			'-v_type',
			'-v_pool_label',
			'-v_close_status',
			'-v_fill_status'
			]
		self.columns = [
			'name',
			'barcode',
			'size',
			'scale',
			'tape_file',
			'status',
			'recycling',
			'location',
			'rule',
			'description',
			'creation_date',
			'backup_date',
			'format',
			'wear_level',
			'recyclable',
			'recycle_age',
			'type',
			'pool_label',
			'close_status',
			'fill_status'
			]
		self.csv_split_count=21
		self.run()
		# the first line is usually the column names
		# so let's remove it
		if self.data[0]['name'] == 'Name':
			del(self.data[0])

	def create_db_pool_entries(self):
		if not self.db:
			print "DB not set"
			return
		print "Creating entries..."
		self._db_start = datetime.datetime.today()
		for id,entry in self.data.iteritems():
			if entry['name'] == 'Name':
				continue
			print "NAME:",entry['name']
			try:
				c = Cartridge.find(
					pool_label=self.pool,
					name=entry['name'])[0]
			except:
				c = Cartridge(
					pool_label=self.pool,
					name=entry['name'],
					barcode=entry['barcode']
				)
				c.save()	
		self._db_end = datetime.datetime.today()
		print "Elapsed:",self._db_end-self._db_start

	def create_db_entries(self):
		if not self.db:
			print "DB not set"
			return
		print "Creating entries..."
		self._db_start = datetime.datetime.today()
		for id,entry in self.data.iteritems():
			c = cartridges(**entry)
			c.blind_create()
		self._db_end = datetime.datetime.today()
		print "Elapsed:",self._db_end-self._db_start


class Tina:

	APPLICATIONS = {	'tina.a52.com.fs':'appl.tina.a52.com.fs',
				'Discreet_2010_Archive':'appl.Discreet_2010_Archive',
				'Discreet_2011_Archive':'appl.Discreet_2011_Archive',
				'flame_archive':'appl.flame_archive',
				}


	def __init__(self,catalog='tina_tina'):
		pass

	@staticmethod
	def log_command(command):
		log.info("Command: %s" % (command))

	@staticmethod
	def tina_find(**kwargs):
		obj = TinaFind(**kwargs)
		try:
			obj.run(verbose=False)
		except TinaError,error:
			#print error.message
			return None
		return obj

	@staticmethod
	def backup(path,dry_run=False,**kwargs):
		obj = TinaBackup(path,**kwargs)
		if dry_run:
			obj.form_command()
			print ("COMMAND: %s" % obj.command)
			log.info("COMMAND: %s" % obj.command)
		else:
			#print "Warning: command would normally run here"
			obj.run(parse=False,verbose=False)
		return obj

	def tina_cart_control(self,**kwargs):
		obj = TinaCartControl(**kwargs)
		obj.run()
		return obj

	@staticmethod
	def get_pool(pool='Discreet_Archive',db=False):
		obj = TinaCartControl()
		if db:
			obj.db=db
		obj.get_pool(pool=pool)
		return obj

	@staticmethod
	def tina_listcart(label,job_ids=False):
		obj = TinaListCart(label,job_ids=job_ids)
		try:
			obj.run()
		except Exception,error:
			if 'unknown from catalog' in error.message:
				message = '%s not in catalog' % label
				raise TinaUnknownCartridgeError,message
			raise
		return obj

	@staticmethod
	def tina_listjob(job_id):
		obj = TinaListJob(job_id)
		obj.run()
		obj.parse_cart_info()
		return obj

	@staticmethod
	def get_label_info(label):
		obj = TinaCartControl()
		obj.get_label_info(label)
		return obj

	@staticmethod
	def erase_cart(label,force=False):
		obj = TinaCartControl()
		obj.erase_cart(label,force=force)
		return obj

	@staticmethod
	def delete_job(job_id):
		obj = TinaODBFree()
		obj.delete_job(job_id)
		return obj

	@staticmethod
	def offline_cart(barcode):
		obj = TinaLibraryControl()
		obj.offline_cart(barcode)
		return obj

	@staticmethod
	def restore(dry_run=False,**kwargs):
		obj = TinaRestore(**kwargs)
		if dry_run:
			obj.form_command()
			log.info("COMMAND: %s" % obj.command)
		else:
			obj.run(parse=False)
		return obj

	@staticmethod
	def parse_year(path):
		regx = re.search('.*([0-9]{2}[A-Z][0-9]{3}).*',path)
		if regx:
			return "20%s" % (regx.group(1)[:2])
		# if we cannot parse the year default to 'misc'
		return 'misc'

	def set_tags(self):
		"""
		Calculate the amount of unneeded
		space on the catalog
		"""
		# first get all the parent directories
		#sel = "select distinct(parent_dir) from catalog where parent_dir!='' and parent_dir='10A226_amazing_race_DA'"
		sel = "select distinct(parent_dir) from catalog where parent_dir!='' and parent_dir!='10A103_Milky_Way_DA_NY'"
		#sel = "select distinct(parent_dir) from catalog where parent_dir!='' and parent_dir='10A103_Milky_Way_DA_NY'"
		result = db.select(database = 'atempo',statement=sel)
		for pdir_row in result:
			pdir = pdir_row['parent_dir']
			# select all the archive files 
			# for this parent directory
			files = {}
			latest = {}
			increment = {}
			duplicate = {}
			dkeys = []
			sel = "select * from catalog where parent_dir='%s' and parent_dir!=''" % pdir
			result2 = db.select(database = 'atempo',statement=sel)
			for fr in result2:
				# look for the latest version of this file
				if not latest.has_key(fr['parent_dir']):
					latest[fr['parent_dir']] = fr
					fr['tag'] = 'latest'
				else:
					if fr['modification_date'] > latest[fr['parent_dir']]['modification_date']:
						latest[fr['parent_dir']]['tag'] = 'incremental'
						latest[fr['parent_dir']] = fr
						fr['tag'] = 'latest'
					else:
						fr['tag'] = 'incremental'

				# look for duplicates of this file
				dup_key = "%s:%s" % (fr['bytes'],time.mktime(fr['modification_date'].timetuple()))
				if dup_key in dkeys:
					if fr['tag'] != 'latest':
						fr['tag'] = 'duplicate'
					else:
						print "WARN: File is a duplicate but is the latest (%s:%s)" % (fr['uid'],fr['parent_dir'])
				else:
					dkeys.append(dup_key)
				files[fr['uid']] = fr

			print "%-7s %-12s %-13s %19s %19s %12s" % ('uid','tag','bytes','mod_date','backup_date','parent_dir')
			for uid,info in files.iteritems():
				print "%-7s %-12s %-13s %19s %19s %12s" % (
					info['uid'],
					info['tag'],
					info['bytes'],
					info['modification_date'],
					info['backup_date'],
					info['parent_dir']
					)
				upd = "update catalog set tag='%s' where uid='%s'" % (info['tag'],info['uid'])
				db.update(database='atempo',statement=upd)

		

	def convert_size(self):
		sel = "select uid,size,scale from catalog"
		result = db.select(database = 'atempo',statement=sel)
		for row in result:
			size = int(row['size'].replace(',',''))
			scale = row['scale']
			if scale == 'KB':
				size = size*1024
			elif scale == 'MB':
				size = size*1024*1024
			upd = "update catalog set bytes='%s' where uid='%s'" % (size,row['uid'])
			db.update(database='atempo',statement=upd)

	def bloat(self):
		sel = "select sum(bytes) from catalog where tag='incremental'"
		inc_bytes = db.select_single(database='atempo',statement=sel)
		sel = "select sum(bytes) from catalog where tag='latest'"
		latest_bytes = db.select_single(database='atempo',statement=sel)
		sel = "select sum(bytes) from catalog where tag='duplicate'"
		dup_bytes = db.select_single(database='atempo',statement=sel)
		print "\nBytes:"
		print "Incremental byte count:",inc_bytes
		print "Duplicate byte count:",dup_bytes
		print "Latest byte count:",latest_bytes
		print "\nScaled:"
		print "Incremental byte count:",numberutil.humanize(int(inc_bytes),scale='bytes')
		print "Duplicate byte count:",numberutil.humanize(int(dup_bytes),scale='bytes')
		print "Latest byte count:",numberutil.humanize(int(latest_bytes),scale='bytes')

	@staticmethod
	def compare_filesizes(x,y,margin=0.99):
		"""
		Return True if x and y are
		within 'margin' of each other.
		"""
		_max = max(x,y)
		_min = min(x,y)
		if _min == _max:
			return True
		if _min == 0 or _max == 0:
			# if one of the values is 0
			# but the other is not, the files
			# should be considered different
			return False
		if float(_min)/float(_max) >= margin:
			return True
		return False

if __name__ == '__main__':
	
	#for obj in TinaObject.find(status='archived'):
	#	print obj.validate_archive()

	#for c in Cartridge.find(name='Discreet_Archive0000200'):
	#for c in Cartridge.find(status='archived',recyclable=0):
	#	print "\nRecycling:",c.data['name']
	#	c.recycle()
	#	c.inspect()
	#for c in Cartridge.find(name='Discreet_Archive0000002'):
	#	ct = c._get_contents_tina()
	#for c in Cartridge.find():
	#	#if 'Discreet' in c.data['name'] and c.data['id_num'] > 438:
	#	if 'Discreet' in c.data['name'] and c.data['id_num'] > 1:
	#		print c.data['name']
	#		c.get_contents()
	#c.recycle()
	#c.get_contents()
	#for c in Cartridge.find(name='Discreet_Archive0000020'):
	#	c.update_status(verbose=True)

	# ----------------------------------------------------------------------
	# TINA CART CONTROL
	# ----------------------------------------------------------------------
	#tcc = TinaCartControl()
	#tcc = tcc.get_pool(db=True)
	##tcc.create_db_pool_entries()
	#for i,info in tcc.data.iteritems():
	#	print info['name'],info['barcode']
	##	c = Cartridge.find(**info)[0]
	##	break

	#latest = TinaFind.find_latest_archive_segment('/2010_archive/10A131_Texas_Lottery_DA/10A131_Texas_Lottery_DA_1.seg')
	#latest = TinaFind.find_latest_archive_segment('/2010_archive/File___/mnt/nas3/2010_archive')
	#print latest
	#print_array(latest)

	# ----------------------------------------------------------------------
	# TINA BACKUP
	# ----------------------------------------------------------------------
	#a = Tina()
	#Tina.tina_backup(path=['/hoop_test/2012_archive/dl_archive_6.seg','/hoop_test/2012_archive/dl_archive_8.seg'],application='Discreet_2010_Archive',strat='B')
	#Tina.tina_backup(path='/hoop_test/2012_archive/dl_archive_6.seg',application='Discreet_2010_Archive',strat='B')

	#o = a.tina_find(path_folder='/2010_archive',recursive=False)
	#o = a.tina_find(path_folder='/hoop_test/2012_archive',application='Discreet_2010_Archive')
	#print o.output


	# ----------------------------------------------------------------------
	# TINA LISTJOB
	# ----------------------------------------------------------------------
	#a = Tina()
	#jids = cart_job_ids.get_job_ids()
	#for jid in jids:
	#	print jid
	#	try: obj = a.tina_listjob(jid)
	#	except:pass
	#	else:
	#		for k,v in obj.data.iteritems():
	#			v['job_id'] = jid
	#			m = job_ids(**v)
	#			m.save()
	#obj = a.tina_listjob('1057')
	#print_array(obj.data)


	# ----------------------------------------------------------------------
	# TINA LISTCART
	# ----------------------------------------------------------------------
	#a = Tina()
	#obj = a.tina_listcart('Discreet_Archive0000057',job_ids=True)
	#print_array(obj.data)

	#a = Tina()
	#ja = {}
	#for cart in consolidation_pools.find():
	#	print "CART:",cart.data['name']
	#	if int(cart.data['id_num']) > 5:
	#		obj = a.tina_listcart(cart.data['name'],job_ids=True)
	#		for k,v in obj.data.iteritems():
	#			v['tape_name'] = cart.data['name']
	#			m = cart_job_ids(**v)
	#			m.save()
	#		time.sleep(1)
	#obj = a.tina_listcart('Discreet_Archive0000663')
	#obj = a.tina_listcart('Discreet_Archive0000572')
	#print_array(obj.data)


	# ----------------------------------------------------------------------
	# TINA FIND
	# ----------------------------------------------------------------------
#	a = Tina()
	#o = a.tina_find(path_folder='A_to_backup/14A100_lowes_spring',application='nas0-taylor.a52.com.fs',list_all=True)
#	o = a.tina_find(path_folder='/A_to_backup/12A212_google_knowing',application='nas0-taylor.a52.com.fs',list_all=True,recursive=True)
	#o = a.tina_find(path_folder='/2010_archive/09A195_Tabloid_DA ',application='tina.a52.com.fs',pattern='09A195_Tabloid_DA',list_all=True)
	#o = a.tina_find(path_folder='/2009_archive/09E150_adidas_2010_DA',list_all=True)
	#o = a.tina_find(path_folder='/2010_archive/11A172_Dodge_Durango_X12_DA',pattern='11A172_Dodge_Durango_X12_DA_12.seg',list_all=True)
	#o = a.tina_find(path_folder='/2010_archive/11A168_Best_Buy_Trade_In_DA',list_all=True)
	##o = a.tina_find(path_folder='/2010_archive',list_all=True)
	##o.db = True
	##o.create_db_entries()
#	o.find_size()
#	print_array(o.data)
	#a.tina_find(path_folder='/2010_archive/10A188_Rainbow_Vfx_DA')
	#a.tina_find(path_folder='/2010_archive')
	#a.tina_find(path_folder='/2010_archive',no_r=True)

	## finding R00938 (Discreet_Archive0000522)
	#bad_cart ='Discreet_Archive0000522'
	#objs = objects.find(cart_name=bad_cart)
	#for obj in objs:
	#	print "PATH:",obj.data['path']
	#	matches = objects.find(path=obj.data['path'])
	#	for m in matches:
	#		if m.data['cart_name'] != bad_cart:
	#			if m.data['modification_date'] == obj.data['modification_date']:
	#				print "\tCopy on:",m.data['cart_name']
	#			else:
	#				print "\tC:",m.data['modification_date']
	#	


	# ----------------------------------------------------------------------
	# TINA RESTORE
	# ----------------------------------------------------------------------
	a = Tina()
	#o = a.tina_find(path_folder='A_to_backup/14A100_lowes_spring',application='nas0-taylor.a52.com.fs',list_all=True)
	# force a restore to fail so I can see the wall of text error message
	a.restore(path_folder='/flame_archive/2014/14A153_Workday_Heart_Archive_2015_SP3/14A153-Workday_Heart_Archive_2015_9.seg',application='appl.flame_archive-X',path_dest='/Volumes/F6412SATA01/tmp',strat='B')
#	tina_restore -folder appl.flame_archive -depth 10Y -mode abort -strat A -path_dest /Volumes/F6412SATA01/holding/2014/14A153_Workday_Heart_Archive_2015_SP3/.restore -path_folder 
#	/flame_archive/2014/14A153_Workday_Heart_Archive_2015_SP3/14A153-Workday_Heart_Archive_2015_9.seg 
# 	-event_to_console





	pass
