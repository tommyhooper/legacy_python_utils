#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import re
from A52.db.orm import Record
from A52.utils import stringutil
from A52.db.dbcontrol import controller
db = controller()

class mailing_lists(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'mailing_lists'
		)
	UNIQUE_KEY = ['project_uid','name']
	VALIDATION ={	'project_uid':{'type':'int','status':'required','unique':False},
				'name':{'type':'string','status':'required','unique':True},
				'date_created':{'type':'date','status':'default','default':'now()'},
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
		Create a project entry in the db
		"""
		# check for necessary parameters:
		if self.data.has_key('uid'):
			raise Exception,'Object already has a uid'
		return self.save()

	def assign_email(self,email_uid):
		"""
		Assign an email_uid to this mailing list
		"""
		print "LIST:%s EMAIL:%s" % (self.data['uid'],email_uid)
		mlp = mailing_list_map(	mailing_list_uid=self.data['uid'],
						email_address_uid=email_uid
						)
		mlp.save()

	def unassign_email(self,email_uid):
		"""
		Assign an email_uid to this mailing list
		"""
		mlp = mailing_list_map.find(	mailing_list_uid=self.data['uid'],
							email_address_uid=email_uid
							)
		if mlp:
			print "Deleting:",mlp[0].data
			mlp[0].delete()


class email_addresses(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'email_addresses'
		)
	VALIDATION ={	'address':{'type':'string','status':'required','unique':True},
				'user_id':{'type':'string','status':'required'},
				'domain':{'type':'string','status':'required'},
				'first_name':{'type':'string'},
				'last_name':{'type':'string'},
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
		Create a project entry in the db
		"""
		# check for necessary parameters:
		if self.data.has_key('uid'):
			raise Exception,'Object already has a uid'
		return self.save()

class mailing_list_map(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'mailing_list_map'
		)
	UNIQUE_KEY = ['mailing_list_uid','email_address_uid']
	VALIDATION ={	'mailing_list_uid':{'type':'int','status':'required'},
				'email_address_uid':{'type':'int','status':'required'},
			}

	def __init__(self,**kwargs):
		"""
		Project Object
		"""
		self.data = {}
		self.data.update(kwargs)

	def create(self):
		"""
		Create a project entry in the db
		"""
		# check for necessary parameters:
		if self.data.has_key('uid'):
			raise Exception,'Object already has a uid'
		return self.save()



if __name__ == '__main__':
	ml = mailing_lists(name='test',project_uid=1)
	ml.save()
	pass



