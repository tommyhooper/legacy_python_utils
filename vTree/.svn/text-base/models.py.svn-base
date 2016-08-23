#!/usr/bin/python

import os
from A52.db.orm import Record

class vUtil:
	def _stat(self):
		"""
		Stat 'path' and add it to self.attributes.
		"""
		stats = os.stat(self.data['path'])
		self.data['st_mode'] = stats.st_mode
		self.data['st_uid'] = stats.st_uid
		self.data['st_gid'] = stats.st_gid

class File(Record,vUtil):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'vTree_files'
		)
	UNIQUE_KEY = ['vTree_uid','path','filenae']
	VALIDATION ={	'vTree_uid':{'type':'vTree','status':'required'},
				'path':{'type':'string','status':'required'},
				'filename':{'type':'string','status':'required'},
				'st_mode':{'type':'int','status':'default','default':17917},
				'st_uid':{'type':'int','status':'default','default':1000},
				'st_gid':{'type':'int','status':'default','default':1000},
				'date':{'type':'date','status':'default','default':'now()'}
			}

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)
		if self.data.has_key('path'):
			if self.data['path']:
				self._stat()

	def create(self):
		"""
		Create a db entry for this file object
		"""
		# check for necessary parameters:
		return self.save()

	def read(self):
		"""
		Read the file contents and store 
		them in self.data['content'] for the db
		"""
		f = open(self.data['path'],mode="rb")
		self.data['content'] = f.read()
		f.close()

class Directory(Record,vUtil):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'vTree_directories'
		)
	UNIQUE_KEY = ['vTree_uid','path']
	VALIDATION ={	'vTree_uid':{'type':'vTree','status':'required'},
				'path':{'type':'string','status':'required'},
				'st_mode':{'type':'int','status':'default','default':17917},
				'st_uid':{'type':'int','status':'default','default':1000},
				'st_gid':{'type':'int','status':'default','default':1000},
				'date':{'type':'date','status':'default','default':'now()'}
			}

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)
		if self.data.has_key('path'):
			if self.data['path']:
				self._stat()

	def create(self):
		"""
		Create a db entry for this directory object
		"""
		# check for necessary parameters:
		return self.save()


class Tree(Record,vUtil):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_production',
		db_table = 'vTrees'
		)
	UNIQUE_KEY = ['department','tree_type','version']
	VALIDATION ={	'department':{'type':'enum','status':'required','choices':['cg','design','compositing']},
				'tree_type':{'type':'enum','status':'required','choices':['project','spot','shot']},
				'version':{'type':'string','status':'default','default':'1.0'},
				'name':{'type':'string','status':'required'},
				'description':{'type':'string','status':'default','default':''},
				'date':{'type':'date','status':'default','default':'now()'}
			}

	def __init__(self,**kwargs):
		self.data = {}
		self.data.update(kwargs)

	def create(self):
		"""
		Create a db entry for this directory object
		"""
		# check for necessary parameters:
		return self.save()


if __name__ == '__main__':
	pass
	x = Tree()
	x.data['name'] = 'eraseme'
	x.data['tree_type'] = 'project'
	x.data['department'] = 'cg'
	x.create()
	x.inspect()
#	f.data['st_mode'] = 10000
#	f.data['st_uid'] = 10000
	#f = File('/home/tmy/src/A52/vTree/samples/CGI/__SHOT__/work.__USER__/maya/workspace.mel')
	#f.read()
	#f.save()



