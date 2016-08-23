

import re,time
from datetime import datetime
from datetime import timedelta
from A52.utils import dateutil

class scheduler:
	"""
	Daemon scheduler class.

	Scheduling events to run at specific times
	of specific days, or to run at specific time intervals
	are all done through this class.

	The class takes a time designation (explained below) and 
	returns the next timestamp that meets the specification.

	Time designation:

	For intervals the designation is a number and letter specifying
	the scale of the interval. The attribute name is 'interval'.
	Examples (all possible scales):
		10s	- 60 seconds
		20m	- 20 minutes
		3h	- 3 hours
		4d	- 4 days
		5w	- 5 weeks
		1y	- 1 year

	For scheduled events the designation is a time in military time
	for the event and a list of days that the event should be run on.
	Two attribute names are used; 'start' and 'days'.
	Examples:
		09:00	['m','w','f']	- 9am on monday, wednesday, and friday
		14:30 ['tu','th']		- 2:30pm on tuesday and thursday
		03:00 ['sa,'su']		- 3am on saturday and sunday
	"""
	def __init__(self,interval=None,start=None,days=None,marker=None):
		self.cfg = {'interval':interval,
				'start':start,
				'days':days}
		self._define_days()
		self._define_interval()
		self._init_marker(marker)
	
	def _init_marker(self,marker):
		"""
		Setup the time marker based on the
		'start' attribute if one is given

		The marker is a datetime object representing
		the next valid time based on the time designation.

		In order for a marker to be 'valid' it must be in the 
		future and exist on an allowed day.

		When a valid marker exists in the past then events that
		are based on this scheduler can be triggered. Once triggered
		the marker must be advanced otherwise the events could be 
		triggered forever.
		"""
		# if the given marker is a datetime object
		# use is and return
		if type(marker).__name__ == 'datetime':
			self.marker = marker
			return
		# if there's no 'start' attribute
		# start right now
		if not self.cfg['start']:
			# form the start time of the marker
			self.marker = datetime.today()
			# since there was no start time we don't want 
			# to advance the marker. this way the current time
			# will be eligible and the requesting method will
			# run() right at it's start
		else:
			# get the hour and minute of the start attribute
			hour = int(self.cfg['start'].split(':')[0])
			minute = int(self.cfg['start'].split(':')[1])
			second = 0
			# form the start time of the marker
			dt = datetime.today()
			self.marker = datetime(	dt.year,dt.month,dt.day,hour,minute,second)
			# now advance the marker to the next eligible time
			# since the start time might take several iterations to catch up
			self._set_next_marker()

	def _advance_marker(self,count=1):
		"""
		Add 'count' interval(s) to the marker
		and return it
		"""
		self.marker+=self.interval
		return self.marker

	def _define_interval(self):
		"""
		Convert the 'interval' attribute into a timedelta instance
		"""
		if not self.cfg['interval']:
			self.cfg['interval'] = 60*60*24
			return 
		num,scale = re.search('([0-9]+)([A-z]+)',str(self.cfg['interval'])).groups()
		num = int(num)
		if scale.lower() == 's':
			delta = timedelta(seconds=num)
			#multiplier = 1
		elif scale.lower() == 'm':
			delta = timedelta(minutes=num)
			#multiplier = 60
		elif scale.lower() == 'h':
			delta = timedelta(hours=num)
			#multiplier = 3600
		elif scale.lower() == 'd':
			delta = timedelta(days=num)
			#multiplier = 3600*24
		elif scale.lower() == 'w':
			delta = timedelta(weeks=num)
			#multiplier = 3600*24*7
		self.interval = delta

	def _define_days(self):
		"""
		Convert the 'days' attribute to list of
		allowed day numbers: 0=sunday, 6=saturday
		"""
		if not self.cfg.has_key('days'):
			self.cfg['days'] = [0,1,2,3,4,5,6]
			return
		ndays = []
		for d in self.cfg['days']:
			if d[0].lower() == 'm':
				ndays.append(1)
			elif d[0].lower() == 'w':
				ndays.append(3)
			elif d[0].lower() == 'f':
				ndays.append(5)
			elif d[0:2].lower() == 'tu':
				ndays.append(2)
			elif d[0:2].lower() == 'th':
				ndays.append(4)
			elif d[0:2].lower() == 'sa':
				ndays.append(6)
			elif d[0:2].lower() == 'su':
				ndays.append(0)
		self.cfg['days'] = ndays
		self.cfg['days'].sort()

	def _set_next_marker(self):
		"""
		Move the marker forward till it's 
		ahead of the current time and return it
		"""
		while not self._validate_marker():
			self._advance_marker()
		return self.marker

	def _validate_marker(self):
		"""
		For a marker to be valid it must be:
		A. in the future, and
		B. exist on one of the 'allowed' days
		"""
		valid = True
		if self.marker < datetime.today():
			valid = False
		if not self.marker.isoweekday() in self.cfg['days']:
			valid = False
		self.valid = valid
		return valid

	def g2g(self):
		"""
		Scheduler check for the current time.
		Return True if the current time is greater
		than the marker, then advance the marker.
		"""
		if self.marker < datetime.today():
			# advance the marker and return True
			return True
		return False

	def advance(self):
		"""
		Advance the marker to the next 
		'valid' datetime
		"""
		self._set_next_marker()

	#@staticmethod
	def predict(interval=None,start=None,days=None):
		"""
		Process the time designation based on the current
		time and return a timestamp for the next occurance 
		"""
		s = scheduler(interval=interval,start=start,days=days)
		return s._set_next_marker()
	predict = staticmethod(predict)






