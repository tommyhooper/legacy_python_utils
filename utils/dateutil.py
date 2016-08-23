import time
import datetime
# TODO: need a python2.3 work around for the decimal module
#from A52.utils import numberutil

DEFAULT_DATETIME_INPUT_FORMATS = (
    '%Y-%m-%d %H:%M:%S',	# '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',		# '2006-10-25 14:30'
    '%Y-%m-%d',			# '2006-10-25'
    '%m-%d-%Y %H:%M:%S',	# '10-25-2006'
    '%m-%d-%Y %H:%M',		# 
    '%m-%d-%Y',			# '10-25-06'
    '%m-%d-%y %H:%M:%S',	# 
    '%m-%d-%y %H:%M',		# 
    '%m-%d-%y',			# '10-25-06'
    '%m/%d/%Y %H:%M:%S',	# '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M',		# '10/25/2006 14:30'
    '%m/%d/%Y',			# '10/25/2006'
    '%m/%d/%y %H:%M:%S',	# '10/25/06 14:30:59'
    '%m/%d/%y %H:%M',		# '10/25/06 14:30'
    '%m/%d/%y',			# '10/25/06'
)
DATETIME_OUTPUT_FORMATS = (
    '%b.%d,%Y',			# 0 	Jan. 5, 2011
    '%H:%M:%S',			# 1 	14:30:59
    '%I:%M:%S %p',		# 2 	02:30:59 PM
    '%Y-%m-%d %H:%M:%S',	# 3 	'2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',		# 4 	'2006-10-25 14:30' (atempo format)
    '%Y-%m-%d',			# 5 	'2006-10-25'
    '%m-%d-%Y %H:%M:%S',	# 6 	'10-25-2006 14:30:59'
    '%m-%d-%Y %H:%M',		# 7	'10-25-2006 14:30'
    '%m-%d-%Y',			# 8 	'10-25-2006'
    '%m-%d-%y %H:%M:%S',	# 9 	'10-25-06 14:30:59'	
    '%m-%d-%y %H:%M',		# 10  	'10-25-06 14:30'	
    '%m-%d-%y',			# 11  	'10-25-06'	
    '%m/%d/%Y %H:%M:%S',	# 12 	'10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M',		# 13 	'10/25/2006 14:30'
    '%m/%d/%Y',			# 14 	'10/25/2006'
    '%m/%d/%y %H:%M:%S',	# 15 	'10/25/06 14:30:59'
    '%m/%d/%y %H:%M',		# 16 	'10/25/06 14:30'
    '%m/%d/%y',			# 17 	'10/25/06'
    '%b.%d,%Y %I:%M %p',	# 18	Jan. 5, 2011 02:30 PM
    '%Y-%m-%d_%H.%M',		# 19 	'2006-10-25_14.30'
    '%y%m%d_%H%M',		# 20 	'110504_1430'
    '%H%M%S',			# 21 	143059
    '%b %d,%Y %I:%M %p',	# 22	Jan. 5, 2011 02:30 PM
    '%H:%M %m/%d/%y ',		# 23 	'14:30 10/25/06'
    '%a %b %d,%Y %I:%M %p',	# 24	Sat. Jan. 5, 2011 02:30 PM
)

def legible_date(date_time=None,format_id=0):
	"""
	Get the current date in a few different formats
	"""
	if not date_time:
		date_time = datetime.datetime.today()
	date_format = DATETIME_OUTPUT_FORMATS[format_id]
	return datetime.datetime.strftime(date_time,date_format)

def get_datetime(format_id=0):
	"""
	Get the current date in a few different formats
	"""
	date_format = DATETIME_OUTPUT_FORMATS[format_id]
	return datetime.datetime.strftime(datetime.datetime.today(),date_format)

def mysql_now():
	"""
	Return the current time in mysql format:
	'%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
	"""
	now = time.time()
	return timestamp_to_datetime(now)

def date_from_string(date_str, input_formats=None):
	input_formats = input_formats or DEFAULT_DATETIME_INPUT_FORMATS
	for format in input_formats:
		try:
			return datetime.datetime(*time.strptime(date_str, format)[0:6])
		except:
			continue
	return None

def hours_diff(date_time_1, date_time_2, format=None):
	"""
	Returns the number of hours between two given times.
	If the times are given as strings, you can pass
	a format identifier
	"""
	if format:
		if type(date_time_1) in [type(str()),type(unicode())]:
			t1 = int(time.mktime(time.strptime(date_time_1,format)))
		else:
			t1 = int(time.mktime(date_time_1.timetuple()))
		if type(date_time_2) in [type(str()),type(unicode())]:
			t2 = int(time.mktime(time.strptime(date_time_2,format)))
		else:
			t2 = int(time.mktime(date_time_2.timetuple()))
	else:
		t1 = int(time.mktime(date_time_1.timetuple()))
		t2 = int(time.mktime(date_time_2.timetuple()))
	hours = round((t2 - t1) / 3600.00, 2)
	return hours
	#return numberutil.accounting_format(hours)

def datetime_to_timestamp(date_time):
	return time.mktime(date_time.timetuple())

def timestamp_to_datetime(timestamp,result='string'):
	if result == 'object':
		return datetime.datetime.fromtimestamp(timestamp)
	else:
		return datetime.datetime.strftime(datetime.datetime.fromtimestamp(timestamp),'%Y-%m-%d %H:%M:%S')
        
def datestamp():
	"""
	Simple format function for all datestamps
	that will show up in the logs.
	"""
	stamp = datetime.datetime.strftime(datetime.datetime.now(),'%b %d %H:%M:%S')
	#stamp = datetime.datetime.strftime(datetime.datetime.now(),'%a %b %d %H:%M:%S')
	return "[%s]" % (stamp)

