#!/usr/bin/env python
# version 1.0
# $Revision: 1.6 $

import MySQLdb
import MySQLdb.cursors
import time
import datetime
import traceback
import sys
from A52 import environment

import logging
log = logging.getLogger(__name__)

# MAIN DB CONTROL FUNCTIONS:
#----------------------------------------------
class controller:
	def __init__(self):
		"""
		Open a single persistent connection for each database
		"""
		self.connections = {}

	def _open_db(self,database):
		if self.connections.has_key(database):
			# test to see if the connection still exists
			try:
				self.connections[database].ping()
			except:
				pass
			else:
				return self.connections[database]
		# get the db host based on the current context
		context = environment.get_context()
		settings = environment.db_settings_for_context(database)
		for dbhost in [settings['host']]:
			try:
				self.connections[database] =MySQLdb.connect(host=dbhost,user='pyre',db=database,cursorclass=MySQLdb.cursors.DictCursor)
			except:
				log.info("Cannot connect to %s" % (dbhost))
				traceback.print_exc(file=sys.stdout)
				pass
			else:
				log.info("Connected to %s" % (dbhost))
				return self.connections[database]

	def _close_db(self,database):
		if self.connections.has_key(database):
			self.connections[database].close()
			del self.connections[database]

	def select(self,database,statement,show_time=0):
		# TODO: pretty sure the MySQLdb has the time 
		# of each call as an attribute - find it
		# and return it based on the 'show_time' arg.
		start_time = time.time()
		db=self._open_db(database)	
		cursor=db.cursor()
		cursor.execute(statement)
		#result=cursor.fetchallDict()
		result=cursor.fetchall()
		self._close_db(db)
#		db.close()
		stop_time = time.time()
		call_time = round(stop_time-start_time,2)
		if show_time:
			print "TIME:",call_time
		return result

	def select_single(self,database,statement):
		db=self._open_db(database)	
		cursor=db.cursor()
		cursor.execute(statement)
		result=cursor.fetchall()
		#db.close()
		self._close_db(db)
		if result:
			return result[0].values()[0]
		else:
			return 0


	def insert_and_return_id(self,database,table,statement):
		db=self._open_db(database)	
		cursor=db.cursor()
		result=cursor.execute(statement)
		id_statement = "select last_insert_id() from %s limit 1" % (table)
		cursor.execute(id_statement)
		new_id=cursor.fetchall()
		uid= int(new_id[0].values()[0])
		db.commit()
		#db.close()
		self._close_db(db)
		return uid

	def insert(self,database,statement):
		db=self._open_db(database)	
		cursor=db.cursor()
		result=cursor.execute(statement)
		db.commit()
		#db.close()
		self._close_db(db)
		return result

	def update(self,database,statement):
		db=self._open_db(database)	
		cursor=db.cursor()
		result=cursor.execute(statement)
		db.commit()
		#db.close()
		self._close_db(db)
		return result

	def delete(self,database,statement):
		db=self._open_db(database)	
		cursor=db.cursor()
		result=cursor.execute(statement)
		db.commit()
		#db.close()
		self._close_db(db)
		return result

	def datetime_to_mysql(self,python_date,round=None):
		"""
		Convert python datetime to mysql format
		the 'round' arguement has these options:
		None - return direct translation (no rounding)
		down - round down to the start of the day (adds 00:00:00 for the timestamp
		up - round up to the end of the day (adds 23:59:59 for the timestamp)
		"""
		if round == 'down':
			return python_date.strftime("%Y-%m-%d 00:00:00")
		elif round == 'up':
			return python_date.strftime("%Y-%m-%d 23:59:59")
		else:
			return python_date.strftime("%Y-%m-%d %H:%M:%S")

if __name__ == '__main__':
	db = db()
	sel = 'select now()'
	time = db.select(database='a52_discreet',statement=sel)
	print "TIME:",time



