#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

from A52.db.validate import valid
from A52.db.orm import Record

class users(Record,valid):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'users'
		)

	def __init__(self):
		"""
		User Object
		"""
		self.data = {}

if __name__ == '__main__':
	pass



