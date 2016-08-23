#!/usr/bin/python

from A52.db.orm import Record

class shots(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'shots'
		)
	UNIQUE_KEY = ['project_uid','name']
	VALIDATION ={	'project_uid':{'type':'int','status':'required','unique':False},
				'spot_uid':{'type':'int','status':'optional','unique':False},
				'name':{'type':'string','status':'required','cleanString':True},
				'created_by':{'type':'user','status':'required','unique':False,'default':'beam'},
				'creation_date':{'type':'date','status':'default','default':'now()'},
				'status':{'type':'enum','status':'default','default':'active','choices':['active','inactive','hold','cancelled','finaled']}
			}

	def __init__(self,**kwargs):
		"""
		Shot Object
		"""
		self.data = {}
		self.data.update(kwargs)
		self.last_error = []

	def create(self):
		"""
		Create a shot entry in the db
		"""
		# check for necessary parameters:
		if self.data.has_key('uid'):
			raise Exception,"Object already has a uid",self.data['uid']
		return self.save()


if __name__ == '__main__':
	pass
