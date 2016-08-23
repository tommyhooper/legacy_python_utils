


#
# 	STAT DAEMON (a52sd)
#
# Define the methods that should be managed by the daemon
# by adding a key to the modules dictionary for each 
# method you want to run as well as the parameters to run it.
# current parameters are:
#	'method'	the method to run
#	'hosts'  	the hosts that should run the method
#	'interval' 	how often the method is run:
#			can be expressed in seconds, minutes, hours,  days, weeks, months
#			e.g. 60s, 20m, 3h, 4d, 1w, 1m
#			Default is seconds
#	'start'	what time the interval is started (military time)
#			eg. '09:00','14:30'
#			Default is immediate
#	'days'	days the method is allowed to run on
#			e.g. 'M','Tu','W','Th','F','Sa','Su'
#			Default is every day
#
# Define the rate at which the daemon loops
#from A52.utils import print_array
RPM = 5

# Define the modules
modules = {}
#from A52.utils.rrd.network import netstat
#modules['network'] = {	'method':netstat,
#				'hosts': ['flame01','flame02','flame03','flame04','flame5','flame6','flame7','flare01','smoke01'],
#				'interval':15}

# SAN: stores the load on each san channel from each hosts's point of view
#from A52.utils.rrd.san import SAN
#modules['san'] = {'method':SAN,
#			'hosts': ['flame01','flame02','flame03','flame04','flare01','smoke01'],
#			'interval': 15 }

# CONCURRENT USERS: stores the # of users on each stone
from A52.utils.rrd.discreet import concurrent_users
modules['concurrent_users'] = {	'method':concurrent_users,
						'hosts': ['bishop'],
						'interval':60} 

# SYNC LIBRARIES: sync the real libraries with the dl_libraries table
#from A52.utils.rrd.discreet import sync_libraries 
#modules['sync_libraries_am'] = {	'method':sync_libraries,
#						'hosts': ['bishop'],
#						'start':'06:00',
#						'interval':'1d'} 
#modules['sync_libraries_pm'] = {	'method':sync_libraries,
#						'hosts': ['bishop'],
#						'start':'16:00',
#						'interval':'1d'} 

# LIBRARY CHECK: check for changed libraries and email dlarchive@a52.com
#from A52.utils.rrd.discreet import library_check
#modules['library_check'] = {		'method':library_check,
#						'hosts': ['none'],
#						'interval':'1d',
#						'start':'04:00',
#						'days':['M','Tu','W','Th','F']} 

# NOTE: Framestore DF is now handled on bishop with a cron
# every 15 minutes. 
# FRAMESTORE DF: stores the disk free on each framestore in the database
#from A52.utils.rrd.discreet import framestore_df
#modules['framestore_df'] = {	'method':framestore_df,
#					'hosts': ['flame01','flame02','flame03','flame04','flare01','smoke01','smack01'],
#					'interval':60} 
#start = 0
#for host in  ['flame01','flame02','flame03','flame04','flare01','smoke01']:
#	modules['fs_df-%s' % host] = {'method':framestore_df,
#						'hosts': [host],
#						'start':'00:%02d' % start,
#						'interval':120} 
#	start+=2

# DB BACKUP: back's up the main A52 database
#from A52.utils.daemon.DBbackup import mysql
#modules['db_backup'] = {	'method':mysql,
#					'hosts': ['bishop','ripley'],
#					'start':'04:00',
#					'interval':'8h'} 

# define the hosts that should monitor the database stats
#modules['db'] = {	'method':None,
#			'hosts': ['bishop','ripley'],
#			'interval':20} 

