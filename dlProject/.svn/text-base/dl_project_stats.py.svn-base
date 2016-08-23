


from A52.db.orm import Record

class dl_project_stats(Record):
	"""
	This is intended as a sub-model to the main
	dlProject model.
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
		self.data.update(kwargs)


