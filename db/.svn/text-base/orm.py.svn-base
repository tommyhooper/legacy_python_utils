import MySQLdb
from MySQLdb.cursors import DictCursor
from types import *
from A52 import utils
from A52.utils import dateutil,print_array
from A52.db import dbConnect,fields
from A52.db.validate import valid

import logging
log = logging.getLogger(__name__)

class InvalidModelException(Exception):
	def __init__(self, model, attribute, value, validator, rule):
		#print attr, value, validator, rule
		self.model = model
		self.attribute = attribute
		self.value = value
		self.validator = validator
		self.rule = rule
		self.message = "'%s' has failed validation. The attriubte '%s'='%s' fails validation:'%s'" % (self.model, self.attribute, self.value, self.validator)

	def __str__(self):
		return self.message
    
class ORMException(Exception):
	pass

_FIELD_CACHE = {}

class Record(object,valid):
	"""
    An abstract base class responsible for the persistence of Objects
    
    @get
    Get a single record
    Record.get(1)
    Record.get(title='A Great Movie', subtitle='Hello')
    
    @find
    Get a list of records where some criteria is true, limit the result to 10 and order by creation_time ASC
    Record.find(status='active', limit=10, order_by='creation_time')
    
    or pass a list to order by
    Record.find(status='active', limit=10, order_by=['status', '-creation_time'])
    
    or perform a where in search
    Record.find(status=['active', 'deleted'], limit=10)
    
    Get a list of records where some criteria is true, limit the result to 10, starting at offset 100 and order by creation_time DESC
    Record.find(status='active', title='A Great Movie', limit=10, offset=100, order_by='-creation_time')
    
    @create
    Create a Record
    record = Record.create(title='A Great Movie')

    record = Record(title='A Great Movie')
    record.save()
    
    @update
    record = Record.get(1)
    record.title = 'A Bad Movie'
    record.save()
    
    @get_or_create
    record = RecordTest.get_or_create(name='test-name-1', description='test-description-1', defaults={'name':'test-name-1', 'description':'test-description-1'})
    record = RecordTest.get_or_create(1, defaults={'name':'test-name-1', 'description':'test-description-1'})

    @find_where
    Perform custom sql lookup, note that you can pass tokens as in the second 2 examples, this is the preferred method
    as passing arguments helps prevent sql injection and allows for native python types to be passed
    
    records = RecordTest.find_where("name ='test-name-1' OR name ='test-name-2'")
    records = RecordTest.find_where("name LIKE %s", ['test-name-%'])
    records = RecordTest.find_where("created_at_date > %s", ['2009-10-10'])
    records = RecordTest.find_where("created_at_date > %s", [datetime object])
        
    @note: 
    You'll notice that often you'll see:   
    self._attrs[fld_name] = val
    rather than:
    setattr(self, fld_name, val)
    
    This is because benchmarks showed that the former method can be as much as 2x faster.
	"""
    
	def __init__(self, is_new=True, **kwargs):
		print "*** ORM INIT ***"
		self._attrs = {}
		self._is_new = is_new
		self._attrs.update(kwargs)
         
#	@classmethod
	def db_table(cls):
		try:
			return cls.DB_ATTRIBUTES['db_table']
		except:
			return (cls.__name__).lower()
        
#	@classmethod
	def db_connection_name(cls):
		try:
			return cls.DB_ATTRIBUTES['db_connection_name']
		except:
			print "Database connection not specified for %s" % cls.__name__
        
#	@classmethod
	def find(cls, **kwargs):
		"""
		Any class that extends this must not use the following attributes
		order_by, limit, offset as these are key words reserved for DB lookups
		"""
		if kwargs:
			where_conditions = []
			limit = ''
			orderby = ''
			offset = ''
			case_sense = ''
			for k in kwargs:
				if k == 'limit': 
					if kwargs[k] == 'last':
						limit = "LIMIT 1"
						orderby = "ORDER BY uid desc"
					else:
						limit = "LIMIT " + str(kwargs[k])
				elif k == 'case_sensitive':
					case_sense = 'COLLATE latin1_bin'
				elif k == 'offset':
					offset = "OFFSET " + str(kwargs[k])
				elif k == 'order_by' and not orderby: 
					order_by_list = []
					# convert string to list so that we don't have to repeat ourselves
					if isinstance(kwargs[k], str):
						fields = [kwargs[k]]
					else:
						fields = kwargs[k]
					for order_by_val in fields:
						sort_order = "ASC"
						if order_by_val.find('-') == 0:
							sort_order = "DESC"
							order_by_val = order_by_val.lstrip('-')
						order_by_list.append("%s %s" % (order_by_val, sort_order))
					orderby = "ORDER BY %s" % (", ".join(order_by_list))
				else:
					if isinstance(kwargs[k], list) and len(kwargs[k]):
						vals = []
						for v in kwargs[k]:
							vals.append("'" + dbConnect.escape(str(v)) + "'")
						where_conditions.append(k + " IN (" + ",".join(vals) + ")")
					elif kwargs[k] == 'NULL':
						where_conditions.append(k + " is " + dbConnect.escape(str(kwargs[k])))
					elif kwargs[k] != None:
						where_conditions.append(k + "='" + dbConnect.escape(str(kwargs[k])) + "'")
			where = ''
			if len(where_conditions): 
				where = "WHERE %s" % (" AND ".join(where_conditions))
			where = "%s %s %s %s %s" % (where, orderby, limit, offset,case_sense)
		else: 
			where = ''
 
		sql = " ".join(["SELECT * FROM", cls.db_table(), where])
		log.info(sql)
		return cls._execute_select(sql)

#	@classmethod
	def find_where(cls, where, tokens=None):
		sql = "SELECT * FROM %s WHERE %s" % (cls.db_table(), where)
		return cls._execute_select(sql, tokens)
    
#	@classmethod
	def _execute_select(cls, sql, tokens=None):
		log.info("ORM: Connected to: %s" % (cls.DB_ATTRIBUTES))
		records = dbConnect.query_connection(cls.db_connection_name(), sql, tokens)
		results = []
		for i in records:
			instance = cls()
			instance.data = i
			results.append(instance)
		return results

	# create a new db record or update and return existing:
#	@classmethod
#	def create(cls,force=False,**kwargs):
#		"""
#		For creating new records, we assume the given 
#		criteria is what designates a unique record. 
#		Therefore, we search for an existing record and 
#		return it if it exists. 
#		"""
#		ex_obj = cls.find(**kwargs)
#		if ex_obj:
#			return ex_obj
#		# create a new record
#		return cls._create(**kwargs)

	def _create(self):
		attrs = []
		values = []
		for k, v in self.data.items():
			if k != 'uid':
				attrs.append(str(k))
				if v == 'now()':
					now = dateutil.mysql_now()
					values.append("'"+dbConnect.escape(str(now))+"'")
				elif v != None:
					values.append("'"+dbConnect.escape(str(v))+"'")
				else:
					values.append("NULL")
		sql = "INSERT INTO %s (%s) VALUES (%s)" % (self.db_table(), ','.join(attrs), ','.join(values))
		log.info("_CREATE: %s" % (sql))
		cursor = dbConnect.query_connection(self.db_connection_name(), sql)
		# if id is passed in then assume we aren't dealing with auto-increment
		uid = cursor.lastrowid
		self.data['uid'] = uid
		self._is_new = False

	def _update(self):
		valid = self.validate()
		values = []
		for k, v in self.data.items():
			if k != 'uid':
				# don't pass null values
				if v != None:
					values.append(str(k) + "='" + dbConnect.escape(str(v)) + "'")
				else:
					values.append(str(k) + "=NULL")
		sql = "UPDATE %s SET %s WHERE uid='%s'" % (self.db_table(), ','.join(values), self.data['uid'])
		log.info(sql)
		dbConnect.query_connection(self.db_connection_name(), sql)
       
	def save(self):
		if self.data.has_key('uid') and self.data['uid']:
			return self._update()
		# validate the data in the object
		# Note this only runs if self.VALIDATION is set
		self.validate()
		# is there a defined unique_key? if so check only for those fields
		if 'UNIQUE_KEY' in dir(self):
			values = []
			for k, v in self.data.items():
				if k in self.UNIQUE_KEY:
					# don't pass null values
					if v != None:
						values.append(str(k) + "='" + dbConnect.escape(str(v)) + "'")
					else:
						values.append(str(k) + "=NULL")
		else:
			# is there an exact duplcate of this record 
			# by exact we mean everything but a creation_date
			# already in the table?
			values = []
			for k, v in self.data.items():
				if k != 'uid':
					if k != 'creation_date':
						# don't pass null values
						if v != None:
							values.append(str(k) + "='" + dbConnect.escape(str(v)) + "'")
						else:
							values.append(str(k) + "=NULL")
		sql = "SELECT uid FROM %s WHERE %s ORDER BY uid DESC LIMIT 1" % (self.db_table(), ' and '.join(values))
		records = dbConnect.query_connection(self.db_connection_name(), sql)
		for row in records:
			self.data['uid'] = row['uid']
			return 

		# if not, create the record
		self._create()
		return 

	def update(self,**kwargs):
		if not self.data.has_key('uid') or not self.data['uid']:
			raise ORMException,"Record cannot be updated: missing uid"
		values = []
		for k, v in kwargs.iteritems():
			if k != 'uid':
				# don't pass null values
				if v != None:
					values.append(str(k) + "='" + dbConnect.escape(str(v)) + "'")
				else:
					values.append(str(k) + "=NULL")
		sql = "UPDATE %s SET %s WHERE uid='%s'" % (self.db_table(), ','.join(values), self.data['uid'])
		log.info(sql)
		dbConnect.query_connection(self.db_connection_name(), sql)

	def delete(self):
		if self.data['uid']:
			dbConnect.query_connection(self.db_connection_name(), "DELETE FROM %s WHERE uid='%s'" % (self.db_table(),self.data['uid']))

	# convenient way to list the contents of an object
	def inspect(self,filter='dict'):
		"""
		print object info
		"""
		print "[44mOBJECT >>>[m"
		if filter == 'full':
			index = {}
			for key in dir(self):
				key_type = type(eval("self.%s" % key))
				try:
					index[key_type][key] = eval("self.%s" % key)
				except:
					index[key_type] = {key:eval("self.%s" % key)}
			utils.print_array(index)
			return 1
		else:
			index = {}
			for key in dir(self):
				key_type = type(eval("self.%s" % key))
				if key_type in [dict,str] and key != "__dict__":
					try:
						index[key_type][key] = eval("self.%s" % key)
					except:
						index[key_type] = {key:eval("self.%s" % key)}
			utils.print_array(index)
			return 1
        

	db_table = classmethod(db_table)
	db_connection_name = classmethod(db_connection_name)
	find = classmethod(find)
	find_where = classmethod(find_where)
#	create = classmethod(create)
	_execute_select = classmethod(_execute_select)

