

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
#		-catalog_only -long -all -depth 10Y -identity root:@52rp3l -display_cart
#
# 	tina_find -path_folder /2010_archive/09A195_Tabloid_DA/ -application tina.a52.com.fs\
#		-pattern "09A195_Tabloid_DA_1.seg" -catalog_only -long  -depth 10Y -identity root:@52rp3l -event_to_console
#
# Environment:
#
#	source /usr/Atempo/tina/.tina.sh 
#
#
#
#
###############################################

import os
import commands
import re
import sys
import datetime
import time
sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import print_array
from A52.utils import numberutil
from models import catalog
from A52.db import controller
db = controller()


class TinaException(Exception):
		pass


class Exec:


	def __init__(self):
		pass

	def _exec(self,command):
		self._exec_start = datetime.datetime.today()
		status,output = commands.getstatusoutput(command)
		self._exec_end = datetime.datetime.today()
		if status > 0:
			message = output
			raise TinaException,message
		return output



class TinaBase(Exec):


	def __init__(self):
		self.csv_split_count = 1

	def source_env(self):
		env_file = '/usr/Atempo/tina/.tina.sh'
		newenvs = commands.getoutput("bash -c 'source %s; env'" % env_file)
		for line in newenvs.split('\n'):
			var = line[0:line.find('=')]
			value = line[line.find('=')+1:]
			os.environ[var] = value

	def run(self):
		# run the find command
		self.find_output = self._exec(self.command)
		# parse the output
		self._parse()

	def form_command(self):
		self.command += " %s " % self.command_options
		if self.__dict__.has_key('args'):
			for k,v in self.args.iteritems():
				if v == True:
					self.command+= " -%s " % (k)
				else:
					self.command+= " -%s %s " % (k,v)
		if self.__dict__.has_key('columns'):
			self.column_key = []
			for k,v in self.columns.iteritems():
				self.column_key.append(k)
				self.command+= " %s " % (v)


	def _parse(self):
		"""
		Split the output from the command into 
		a dictionary.
		"""
		print "Parsing output..."
		self._parse_start = datetime.datetime.today()
		data = {}
		split_lines = self.find_output.split('\n')
		print "TOTAL LINES:",len(split_lines)
		i = 0
		for line in split_lines:
			print "LEN:",len(line.split(';'))
			if len(line.split(';')) == self.csv_split_count:
				data[i] = self._split_csv_line(line)
				i+=1
		self.data = data
		self._parse_end = datetime.datetime.today()
		print "Elapsed:",self._parse_end-self._parse_start

	def _split_csv_line(self,line):
		split = line.split(';')
		info = {}
		for i in range(0,len(self.column_key),1):
			info[self.column_key[i]] = split[i]
		return info


class TinaFind(Exec):


	def __init__(self,**kwargs):
		self.command = "tina_find"
		self.application = 'tina.a52.com.fs'
		self.args = kwargs
		self.data = {}
		self.db = False
		# precompile and store some regex's that
		# we'll use to recognize different types
		# of output lines from the tina commands
		#regx = re.search('^(|.*[^0-9])([0-9]+)([^0-9]*)$',filename)
		self.re = {
			'event_line':re.compile("^[0-9]* *[A-Z]* *[A-z]* *[A-z]* *[0-9]* *[0-9]{2}:[0-9]{2}:[0-9]{2} *[0-9]{4} *\"[A-z]*:"),
			'csv_line':re.compile("^[A-z]*;[0-9]*;[0-9]*;[0-9,]*"),
			'text_short':re.compile("^([A-z]*) *([0-9]*) *([0-9]*) *([0-9,]*) *([A-z]{3}) *([A-z]{3}) *([0-9]+) *([0-9]{2}:[0-9]{2}:[0-9]{2}) *([0-9]{4}) *(.*[^ ]) *(\[.*)"),
			'text_long':re.compile("^([A-z]*) *([0-9]*) *([0-9]*) *([0-9,]*) *([A-z]{3}) *([A-z]{3}) *([0-9]+) *([0-9]{2}:[0-9]{2}:[0-9]{2}) *([0-9]{4}) *([A-z]{3}) *([A-z]{3}) *([0-9]+) *([0-9]{2}:[0-9]{2}:[0-9]{2}) *([0-9]{4}) *(.*[^ ]) *(\[.*)"),
			}

		self.parse_args()
		self.form_command()
		env_file = '/usr/Atempo/tina/.tina.sh'
		newenvs = commands.getoutput("bash -c 'source %s; env'" % env_file)
		for line in newenvs.split('\n'):
			var = line[0:line.find('=')]
			value = line[line.find('=')+1:]
			os.environ[var] = value
		#if run:
		#	self.run()

	def parse_args(self):
		"""
		Keyword arguements are turned into
		command line arguements:
			host='tina' 	-> 	-host tina
		for arguements that have no variables:
			catalog_only=True -> 	-catalog_only
		"""
		# set some defaults
		if not self.args.has_key('application'):
			self.args['application'] = self.application
		if not self.args.has_key('catalog_only'):
			self.args['catalog_only'] = True
		if not self.args.has_key('depth'):
			self.args['depth'] = '10Y'
		if not self.args.has_key('all'):
			self.args['all'] = True
		if not self.args.has_key('long'):
			self.args['long'] = True
		if not self.args.has_key('display_cart'):
			self.args['display_cart'] = True
		if not self.args.has_key('event_to_console'):
			self.args['event_to_console'] = True
		if not self.args.has_key('output_format'):
			self.args['output_format'] = 'csv'
		if not self.args.has_key('application') and not self.args.has_key('host'):
			self.args['application'] = self.application

	def form_command(self):
		for k,v in self.args.iteritems():
			if v == True:
				self.command+= " -%s " % (k)
			else:
				self.command+= " -%s %s " % (k,v)

	def run(self):
		# run the find command
		self.find_output = self._exec(self.command)
		# parse the output
		self._parse()

	def create_db_entries(self):
		print "Creating entries..."
		if self.db:
			self._db_start = datetime.datetime.today()
			for id,entry in info['archive'].iteritems():
				c = catalog(**entry)
				#c.blind_create()
				#c.save()
			self._db_end = datetime.datetime.today()
			print "Elapsed:",self._db_end-self._db_start

	def _parse(self):
		"""
		Split the output from tina_find into 
		a dictionary.
		NOTE:
		  'filename' will always be split 
		   into 3 important parts:
			/<base_dir>/<parent_dir>/<relative_path>...
		"""
		print "Parsing output..."
		self._parse_start = datetime.datetime.today()
		archive = {}
		events = {}
		split_lines = self.find_output.split('\n')
		print "TOTAL LINES:",len(split_lines)
		lc = 0
		ec = 0
		for line in split_lines:
			if re.match(self.re['event_line'],line):
				events[ec] = line
				ec+=1
			elif re.match(self.re['csv_line'],line):
				if len(line.split(';')) > 10:
					archive[lc] = self._split_csv_long_line(line)
				else:
					archive[lc] = self._split_csv_short_line(line)
			else:

				match = re.match(self.re['text_long'],line)
				if match:
					archive[lc] = self._split_long_line(match)
				else:
					match = re.match(self.re['text_short'],line)
					if match:
						archive[lc] = self._split_short_line(match)
					else:
						print "UNKNOWN:",line
						lc-=1
			lc+=1
		self.data = archive
		self.events = events
		self._parse_end = datetime.datetime.today()
		print "Elapsed:",self._parse_end-self._parse_start

	def _split_short_line(self,match):
		#file 182020         100         6,787,645,440   Wed Aug  3 02:12:36 2011    /2010_archive/11A168_Best_Buy_Trade_In_DA/11A168_Best_Buy_Trade_In_DA_6.seg [Discreet_Archive0000572]
		base_dir,parent_dir,relative_path = ['','','']
		filename = match.group(10).lstrip('/').split('/')
		if len(filename) > 0:
			base_dir = filename[0]
		if len(filename) > 1:
			parent_dir = filename[1]
		if len(filename) > 2:
			relative_path = "/".join(filename[2:])
		return {	'object_type':match.group(1),
				'user_id':match.group(2),
				'group_id':match.group(3),
				'size':match.group(4),
				'arc_weekday':match.group(5),
				'arc_month':match.group(6),
				'arc_day':match.group(7),
				'arc_time':match.group(8),
				'arc_year':match.group(9),
				'base_dir':base_dir,
				'parent_dir':parent_dir,
				'relative_path':relative_path,
				'cartridges':match.group(11),
				}

	def _split_long_line(self,line):
		#file 182020         100         6,787,645,440   Tue Aug  2 22:05:04 2011 Wed Aug  3 02:12:36 2011      /2010_archive/11A168_Best_Buy_Trade_In_DA/11A168_Best_Buy_Trade_In _DA_6.seg [Discreet_Archive0000572, Discreet_Archive0000572]
		base_dir,parent_dir,relative_path = ['','','']
		filename = match.group(15).lstrip('/').split('/')
		if len(filename) > 0:
			base_dir = filename[0]
		if len(filename) > 1:
			parent_dir = filename[1]
		if len(filename) > 2:
			relative_path = "/".join(filename[2:])
		return {	'object_type':match.group(1),
				'user_id':match.group(2),
				'group_id':match.group(3),
				'size':match.group(4),
				'mod_weekday':match.group(5),
				'mod_month':match.group(6),
				'mod_day':match.group(7),
				'mod_time':match.group(8),
				'mod_year':match.group(9),
				'arc_weekday':match.group(10),
				'arc_month':match.group(11),
				'arc_day':match.group(12),
				'arc_time':match.group(13),
				'arc_year':match.group(14),
				'base_dir':base_dir,
				'parent_dir':parent_dir,
				'relative_path':relative_path,
				'cartridges':match.group(16),
				}

	def _split_csv_long_line(self,line):
		#file;182020;100;6,473;MB;2011-08-03 02:12;;;/2010_archive/11A168_Best_Buy_Trade_In_DA/11A168_Best_Buy_Trade_In_DA_6.seg; [Discreet_Archive0000572]
		split = line.split(';')
		base_dir,parent_dir,relative_path = ['','','']
		filename = split[10].lstrip('/').split('/')
		if len(filename) > 0:
			base_dir = filename[0]
		if len(filename) > 1:
			parent_dir = filename[1]
		if len(filename) > 2:
			relative_path = "/".join(filename[2:])
		return {	'object_type':split[0],
				'user_id':split[1],
				'group_id':split[2],
				'size':split[3],
				'scale':split[4],
				'backup_date':split[5],
				'unknown_a':split[6],
				'unknown_b':split[7],
				'base_dir':base_dir,
				'parent_dir':parent_dir,
				'relative_path':relative_path,
				'cartridges':split[9]}

	def _split_csv_long_line(self,line):
		#file;182020;100;6,473;MB;2011-08-02 22:05;2011-08-03 02:12;;;;/2010_archive/11A168_Best_Buy_Trade_In_DA/11A168_Best_Buy_Trade_In_DA_6.seg; [Discreet_Archive0000572]
		split = line.split(';')
		base_dir,parent_dir,relative_path = ['','','']
		filename = split[10].lstrip('/').split('/')
		if len(filename) > 0:
			base_dir = filename[0]
		if len(filename) > 1:
			parent_dir = filename[1]
		if len(filename) > 2:
			relative_path = "/".join(filename[2:])
		return {	'object_type':split[0],
				'user_id':split[1],
				'group_id':split[2],
				'size':split[3],
				'scale':split[4],
				'modified_date':split[5],
				'backup_date':split[6],
				'unknown_a':split[7],
				'unknown_b':split[8],
				'offline':split[9],
				'base_dir':base_dir,
				'parent_dir':parent_dir,
				'relative_path':relative_path,
				'cartridges':split[11]}


class TinaListCart(TinaBase):
	"""
	tina_listcart -label Discreet_Archive0000663 -v_type -v_path -v_backup_date -v_modification_date -v_info_cart -v_folder -output_format csv
	"""


	def __init__(self,label):
		self.label = label
		self.source_env()
		self.data = {}
		self.db = False
		self.command = "tina_listcart"
		self.command_options = " -output_format csv -label %s" % self.label
		self.columns = {
			'type':'-v_type',
			'path':'-v_path',
			'backup_date':'-v_backup_date',
			'modification_date':'-v_modification_date',
			'info_cart':'-v_info_cart',
			'folder':'-v_folder'
			}
		self.form_command()
		self.csv_split_count=9


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


	def __init__(self,pool='Discreet_Archive'):
		self.pool = pool
		self.data = {}
		self.db = False
		self.command = "tina_cart_control"
		self.command_options = "-pool %s -list -output_format csv" % self.pool
		self.columns = { 
			'name':'-v_name',
			'barcode':'-v_barcode',
			'size':'-v_volume',
			'scale':'-v_unit',
			'tape_file':'-v_tape_file',
			'status':'-v_status',
			'recyling':'-v_recycling',
			'location':'-v_location',
			'rule':'-v_rule',
			'description':'-v_description',
			'creation_date':'-v_creation_date',
			'backup_date':'-v_backup_date',
			'format':'-v_format',
			'wear_level':'-v_wear_level',
			'recyclable':'-v_recyclable',
			'recycle_age':'-v_recycle_age',
			'type':'-v_type',
			'pool_label':'-v_pool_label',
			'close_status':'-v_close_status',
			'fill_status':'-v_fill_status',
			}
		self.form_command()
		self.source_env()
		self.csv_split_count=21

	def _split_csv_long_line(self,line):
		split = line.split(';')
		info = {}
		for i in range(0,len(self.column_key),1):
			info[self.column_key[i]] = split[i]
		return info



class Atempo:


	def __init__(self,catalog='tina_tina'):
		# main catalog for a52 is 'tina_tina'
		#self.host = 'tina'
		#self.user = 'root'
		#self.passwd = '******'
		#self.application = 'tina.a52.com.fs'
		# source the atempo environment file
		# we're letting a bash shell do the 
		# sourcing then just stealing the
		# env variables after
		env_file = '/usr/Atempo/tina/.tina.sh'
		newenvs = commands.getoutput("bash -c 'source %s; env'" % env_file)
		for line in newenvs.split('\n'):
			var,value = line.split('=')
			os.environ[var] = value

	def tina_find(self,**kwargs):
		obj = TinaFind(**kwargs)
		obj.run()
		print_array(obj.data)

	def tina_cart_control(self,**kwargs):
		obj = TinaCartControl(**kwargs)
		obj.run()
		print_array(obj.data)

	def tina_listcart(self,label):
		obj = TinaListCart(label)
		obj.run()
		print_array(obj.data)

	def set_tags(self):
		"""
		Calculate the amount of unneeded
		space on the catalog
		"""
		# first get all the parent directories
		#sel = "select distinct(parent_dir) from catalog where relative_path!='' and parent_dir='10A226_amazing_race_DA'"
		#sel = "select distinct(parent_dir) from catalog where relative_path!='' and parent_dir!='10A103_Milky_Way_DA_NY'"
		sel = "select distinct(parent_dir) from catalog where relative_path!='' and parent_dir='10A103_Milky_Way_DA_NY'"
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
			sel = "select * from catalog where parent_dir='%s' and relative_path!=''" % pdir
			result2 = db.select(database = 'atempo',statement=sel)
			for fr in result2:
				# look for the latest version of this file
				if not latest.has_key(fr['relative_path']):
					latest[fr['relative_path']] = fr
					fr['tag'] = 'latest'
				else:
					if fr['modified_date'] > latest[fr['relative_path']]['modified_date']:
						latest[fr['relative_path']]['tag'] = 'incremental'
						latest[fr['relative_path']] = fr
						fr['tag'] = 'latest'
					else:
						fr['tag'] = 'incremental'

				# look for duplicates of this file
				dup_key = "%s:%s" % (fr['bytes'],time.mktime(fr['modified_date'].timetuple()))
				if dup_key in dkeys:
					if fr['tag'] != 'latest':
						fr['tag'] = 'duplicate'
					else:
						print "WARN: File is a duplicate but is the latest (%s:%s)" % (fr['uid'],fr['relative_path'])
				else:
					dkeys.append(dup_key)
				files[fr['uid']] = fr

			print "%-7s %-12s %-13s %19s %19s %12s" % ('uid','tag','bytes','mod_date','backup_date','relative_path')
			for uid,info in files.iteritems():
				print "%-7s %-12s %-13s %19s %19s %12s" % (
					info['uid'],
					info['tag'],
					info['bytes'],
					info['modified_date'],
					info['backup_date'],
					info['relative_path']
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

if __name__ == '__main__':
	#start = datetime.datetime.today()
	a = Atempo()
	a.tina_listcart('Discreet_Archive0000663')
#	a.tina_cart_control()



#	a.tina_find(path_folder='/2010_archive/11A168_Best_Buy_Trade_In_DA')
	
#	obj = TinaFind(path_folder='/2010_archive/11A168_Best_Buy_Trade_In_DA')
#	obj.run()

#	a.tina_find(path_folder='/2010_archive/10A188_Rainbow_Vfx_DA',catalog_only=True,depth='10Y',event_to_console=True,all=True,display_cart=True,long=True)
#	a.tina_find(path_folder='/2010_archive',catalog_only=True,depth='10Y',event_to_console=True,all=True,display_cart=True,long=True,no_r=True)
#	a.tina_find(path_folder='/2010_archive',catalog_only=True,depth='10Y',event_to_console=True,all=True,display_cart=True,long=True)
	#end = datetime.datetime.today()
	#print end-start
	pass


