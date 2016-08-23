#!/usr/bin/python

from A52.db.orm import Record

class spots(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'spots'
		)
	UNIQUE_KEY = ['project_uid','name']
	VALIDATION ={	'project_uid':{'type':'int','status':'required','unique':False},
				'name':{'type':'string','status':'required','cleanString':True},
				'created_by':{'type':'user','status':'required','unique':False,'default':'beam'},
				'producer':{'type':'user','status':'optional','unique':False},
				'start_date':{'type':'date','status':'default','unique':False,'default':'now()'},
				'creation_date':{'type':'date','status':'default','default':'now()'},
				'status':{
					'type':'enum',
					'status':'default',
					'default':'active',
					'choices':['active','inactive','hold','cancelled','finalled','deleted']
					}
			}

	def __init__(self,**kwargs):
		"""
		Project Object
		"""
		self.data = {}
		self.data.update(kwargs)
		self.last_error = []

	def create(self):
		"""
		Create a spot entry in the db
		"""
		# check for necessary parameters:
		#error = self._validate_settings()
		if self.data.has_key('uid'):
			raise Exception,"Object already has a uid"
		return self.save()


if __name__ == '__main__':
	pass
