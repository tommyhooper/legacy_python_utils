#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import re
from datetime import datetime
from datetime import timedelta
from A52.utils import numberutil
from A52.utils import dateutil
from A52.db.orm import Record
from A52.db import controller
db = controller()

class framestores(Record):
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_discreet',
		db_table = 'framestores'
		)
	# This table does not have any unique
	# restrictions as many entries can point
	# to the same framestore without causing issues
	#UNIQUE_KEY = ['host','volume']
	volume_re = re.compile('^stonefs[0-7]$')
	UNIQUE_KEY = ['name','status']
	VALIDATION ={	'name':{'type':'string','status':'required'},
				'host':{'type':'string','status':'required'},
				'volume':{'type':'string','status':'required','validate_re':volume_re},
				'mount_name':{'type':'string','status':'required'},
				'bytes_total':{'type':'int','status':'default','default':0},
				'bytes_free':{'type':'int','status':'default','default':0},
				'partition':{'type':'range','status':'required','range':(0,7)},
				'host_limit':{'type':'int','status':'default','default':3},
				'status':{'type':'enum','status':'default','default':'active','choices':['active','inactive']}
			}

	def __init__(self):
		"""
		Framestore Object
		"""
		pass

	#@staticmethod
	def find_uid(name):
		fs = framestores.find(name=name)
		if fs:
			return fs[0].data['uid']
	find_uid = staticmethod(find_uid)

	def create(self):
		"""
		Create a record in the db for a framestore
		"""
		# check for necessary parameters:
		return self.save()

	def format_df(self):
		"""
		Calculate some space attributes and attach 
		them to the object
		"""
		self.host_text = "%s (%s)" % (self.data['name'],self.data['host'])
		if self.data['bytes_total']:
			self.bytes_used = self.data['bytes_total'] - self.data['bytes_free']
			self.bytes_free = self.data['bytes_free']
			self.bytes_total = self.data['bytes_total']
			self.dsp_bytes_used = numberutil.humanize(self.bytes_used)
			self.dsp_bytes_total = numberutil.humanize(self.data['bytes_total'])
			self.dsp_bytes_free = numberutil.humanize(self.data['bytes_free'])
			self.fraction_used = (self.bytes_used*1.0) / (self.data['bytes_total']*1.0)
			self.percent_used = int(round(self.fraction_used*100,0))
			self.capacity_text = "%s%% Used    %s free   (%s total)" % (self.percent_used,self.dsp_bytes_free,self.dsp_bytes_total)
		else:
			self.bytes_used = 0
			self.bytes_free = 0
			self.bytes_total = 0
			self.dsp_bytes_total = '0'
			self.dsp_bytes_used = '0'
			self.dsp_bytes_free = '0'
			self.fraction_used = 0
			self.percent_used = 0
			self.capacity_text = ''
		self.display_text = "%s %s" % (self.host_text,self.capacity_text)

	#@staticmethod
	def df_all():
		"""
		Get the current capacity stats on each
		'active' framestore (from the db)
		"""
		stones = framestores.find(status='active')
		for stone in stones:
			stone.format_df()
		return stones
	df_all = staticmethod(df_all)


class dl_project_stats(Record):
	"""
	Since the Framestore class often deals
	with project stats we put the 
	dl_project_stats model here.
	"""
	DB_ATTRIBUTES = dict(
		db_connection_name = 'a52_discreet',
		db_table = 'dl_project_stats'
		)
	# the UNIQUE_KEY defines fields that make a record unique
	# no new record can be created if those fields are a match
	UNIQUE_KEY = ['host','volume','dl_project_name']
	VALIDATION ={	'host':{'type':'string','status':'required'},
				'volume':{'type':'string','status':'required'},
				'dl_project_name':{'type':'string','status':'required'},
				'frames':{'type':'int','status':'default','default':0},
				'bytes':{'type':'int','status':'default','default':0},
				'poll_date':{'type':'date','status':'default','default':'now()'},
			}

	def __init__(self,**kwargs):
		self.data = {}
		for k in self.VALIDATION:
			self.data[k] = None
		self.data.update(kwargs)

	def __getattr__(self,name):
		if name == 'bytes_self':
			self.format_df()
			return self.bytes_self
		if name == 'bytes_shared':
			self.format_df()
			return self.bytes_shared
		if name == 'bytes_total':
			self.format_df()
			return self.bytes_total
		if name == 'dsp_bytes_self':
			self.format_df()
			return self.dsp_bytes_self
		if name == 'dsp_bytes_shared':
			self.format_df()
			return self.dsp_bytes_shared
		if name == 'dsp_bytes_total':
			self.format_df()
			return self.dsp_bytes_total
		if name == 'current':
			return self.is_current()
		if name == 'frames_self':
			self.format_df()
			return self.frames_self
		if name == 'frames_shared':
			self.format_df()
			return self.frames_shared
		if name == 'frames_total':
			self.format_df()
			return self.frames_total
		if name == 'dsp_poll_date':
			self.format_df()
			return self.dsp_poll_date
		message = "'Framestore' has no attribute %s" % name
		raise AttributeError,message

	def is_current(self,days=1):
		"""
		Return True if the poll_date is
		within 'days'
		"""
		today = datetime.today()
		if self.data['poll_date']:
			if today - self.data['poll_date'] > timedelta(days=days):
				return False
		return True

	def format_df(self):
		"""
		Calculate some space attributes and attach 
		them to the object
		"""
		if not self.data.has_key('bytes'):
			self.data['bytes'] = None
		try:
			self.frames_self = self.data['frames']
			self.frames_shared = self.data['frames_shared']
			self.frames_total = self.data['frames'] + self.data['frames_shared']
			self.bytes_self = self.data['bytes']
			self.bytes_shared = self.data['bytes_shared']
			self.bytes_total = self.data['bytes'] + self.data['bytes_shared']
			self.dsp_bytes_self = numberutil.humanize(self.bytes_self,scale='bytes')
			self.dsp_bytes_shared = numberutil.humanize(self.bytes_shared,scale='bytes')
			self.dsp_bytes_total = numberutil.humanize(self.bytes_total,scale='bytes')
			self.dsp_poll_date = dateutil.legible_date(self.data['poll_date'],16)
		except:
			self.frames_self = 0
			self.frames_shared = 0
			self.frames_total = 0
			self.bytes_self = 0
			self.bytes_shared = 0
			self.bytes_total = 0
			self.dsp_bytes_self = '0'
			self.dsp_bytes_shared = '0'
			self.dsp_bytes_total = '0'
			self.dsp_poll_date = ''



if __name__ == '__main__':
#	print framestores.df_all()
#	fs = Framestore.find(uid=1)
#	for f in fs:
#		f.inspect()
#	f = Framestore.find(uid=1,limit='last')
#	print "F:",f[0].data
	pass


