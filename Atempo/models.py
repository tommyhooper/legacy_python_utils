#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

from A52 import settings
from A52 import environment
from A52.db.orm import Record
from A52.utils import print_array
from A52.db import controller
db = controller()
import traceback
import logging
log = logging.getLogger(__name__)

class catalog(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'catalog'
		)
	# the UNIQUE_KEY defines files that make a record unique
	# no new record can be created if those fields are a match
	#UNIQUE_KEY = []
	VALIDATION = {	'object_type':{'type':'text','status':'required'},
				'user_id':{'type':'int','status':'required'},
				'group_id':{'type':'int','status':'required'},
				'size':{'type':'string','status':'required'},
				'scale':{'type':'string','status':'required'},
				'modified_date':{'type':'date','status':'required'},
				'backup_date':{'type':'date','status':'required'},
				'unknown_a':{'type':'string','status':'default','default':''},
				'unknown_b':{'type':'string','status':'default','default':''},
				'offline':{'type':'string','status':'default','default':''},
				'base_path':{'type':'text','status':'required'},
				'parent_dir':{'type':'text','status':'default','default':''},
				'relative_path':{'type':'text','status':'default','default':''},
				'cartridges':{'type':'text','status':'required'},
			}

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into catalog set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)
			
	def create(self):
		"""
		Create a dl project and add
		it in the database
		"""
		print "Creating catalog entry"
		if self.data.has_key('uid'):
			del(self.data['uid'])
		valid = self.save()
		if not valid[0]:
			message = "catalog: Could not validate settings:",(valid[1])
			print message
			self.last_error = valid[1]
			return (False,message)
		return self.save()


class cartridges(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'cartridges'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into cartridges set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)


class objects(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'objects'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into objects set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)
			
class consolidation_pools(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'consolidation_pools'
		)

	def __init__(self,**kwargs):
		self.data = kwargs
		#self._convert_tape_id()

	def reduce_args(self):
		"""
		Remove non-field args from self.data
		"""
		sel = "describe consolidation_pools"
		desc = db.select(database='atempo',statement=sel)
		fields = [f['Field'] for f in desc]
		valid_data = {}
		for k,v in self.data.iteritems():
			if k in fields:
				valid_data[k] = v
		self.data = valid_data

	def _convert_tape_id(self):
		"""
		Grab the number out of the tape_id
		"""
		try:
			self.data['id_num'] = int(''.join([c for c in self.data['name'] if c.isdigit()]))
		except:
			traceback.print_exc()
			pass

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into consolidation_pools set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)

	@staticmethod
	def current(pool='Discreet_Archive'):
		"""
		Find the current cartridge
		in the given 'pool'.

		The current cartridge is the lowest
		numbered (id_num) cartridge that is 
		either 'in_progress' or 'pending'
		"""
		sel = """	select *
				from
					consolidation_pools
				where
					status='in_progress'
					or status='pending'
				order by
					id_num
				limit 1
			"""
		records = db.select(database='atempo',statement=sel)
		for row in records:
			obj = consolidation_pools(**row)
			return obj
	
	def change_status(self,status):
		"""
		Change the status of an entry.
		"""
		if status:
			self.data['status'] = status
			self.save()

			
class consolidation_files(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'consolidation_files'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into consolidation_files set %s" % (",".join(seg))
		result = db.select(database='atempo',statement=ins)

	def change_status(self,status):
		upd = """	update 
					consolidation_files 
				set 
					status='%s' 
				where 
					uid='%s'
			""" % (status,self.data['uid'])
		db.update(database='atempo',statement=upd)

	def consolidated(self):
		"""
		Check for any instance of the
		current file that has been processed.
		This means any entry matching the 
		current parent_dir and filename that
		is not 'pending' or 'duplicate'.
		"""
		sel = """	select 
					count(*) 
				from 
					consolidation_files
				where binary
					parent_dir='%s'
					and filename='%s'
					and status!='pending'
					and status!='duplicate'
			""" % (	self.data['parent_dir'],
					self.data['filename'])
		count = db.select_single(database='atempo',statement=sel)
		if count > 0:
			return True
		return False

	@staticmethod
	def status():
		"""
		Get status counts for all files
		in the consolidation_files table.


		"""
		sel = """	select 
					distinct(status) as status,
					count(status) as count
				from 
					consolidation_files 
				group by 
					status
			"""
		return db.select(database='atempo',statement=sel)


class job_id_files(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'job_id_files'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into job_id_files set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)

class job_ids(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'job_ids'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into job_ids set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)



class cart_job_ids(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'atempo',
		db_table = 'cart_job_ids'
		)

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def blind_create(self):
		seg = []
		for k,v in self.data.iteritems():
			seg.append("%s='%s'" % (k,v))
		ins = "insert into cart_job_ids set %s" % (",".join(seg))
		result = db.select(database = 'atempo',statement=ins)

	@staticmethod
	def get_job_ids():
		job_ids = []
		sel = "select distinct(job_id) from cart_job_ids"
		for row in db.select(database = 'atempo',statement=sel):
			job_ids.append(int(row['job_id']))
		job_ids.sort()
		return job_ids


if __name__ == '__main__':

	import sys
	duplicates = {}
	for e in consolidation_files.find(status='restored'):
		key = "%s/%s" % (e.data['parent_dir'],e.data['filename'])
		try:
			duplicates[key].append(e)
		except:
			duplicates[key] = [e]
		

	for k,v in duplicates.iteritems():
		print [y.data['uid'] for y in v]
		for e in sorted(v,key=lambda x: x.data['uid'])[1:]:
			print "  >",e.data['uid']
			e.data['status'] = 'duplicate_restore'
			e.save()

	sys.exit()

	for e in consolidation_files.find(status='restored'):
		sel = """	select 
					count(*)
				from 
					consolidation_files 
				where binary
					parent_dir='%s'
					and filename='%s'
					and status!='pending'
			""" % (e.data['parent_dir'],e.data['filename'])
		count = db.select_single(database='atempo',statement=sel)
#					distinct(status)
#		sts = db.select(database='atempo',statement=sel)
#		if sts:
#			print e.data['path']
#			for s in sts:
#				print "  %s" % s['status']
		if int(count) > 0:
			print "-"*120
			print "  %s: %18s :[34m%12s[m: %s" % (e.data['uid'],e.data['tape_id'],e.data['status'],e.data['path'])
			s2 = """	select 
						uid,tape_id,path,status
					from 
						consolidation_files 
					where binary
						parent_dir='%s'
						and filename='%s'
						and status!='pending'
				""" % (e.data['parent_dir'],e.data['filename'])
			for row in db.select(database='atempo',statement=s2):
				print "  %s: %18s :%12s: %s" % (row['uid'],row['tape_id'],row['status'],row['path'])
#			break

#| archived      |
#| duplicate     |
#| interceded    |
#| skip          |
#| archive_error |
#| restored      |
#| directory     |
#| pending       |
#| compare_error |
#| invalid_path  |


#	obj = consolidation_pools(name='Discreet_Archive0000005')

#	for obj in consolidation_pools.find():
#		if not obj.data['id_num']:
#			obj._convert_tape_id()
#			obj.save()
#			print obj.data['id_num']
			
#	obj.inspect()
	pass

