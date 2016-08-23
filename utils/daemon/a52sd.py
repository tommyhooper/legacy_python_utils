#!/usr/bin/env python

from A52.utils.daemon import Daemon
import time
import socket
import os
import sys
import traceback
from A52 import environment
environment.set_context('live')
import settings
from scheduler import scheduler
from A52.utils import print_array
#from A52 import Log
#log = Log.create_log('a52sd.log')
import logging, logging.handlers
log = logging.getLogger('a52sd')
#timestamp_formatter = logging.Formatter("%(asctime)s %(name)s: %(levelname)s: %(message)s")
##logfile_handler = logging.FileHandler('/var/log/a52sd.log')
#logfile_handler = logging.handlers.RotatingFileHandler('/var/log/a52sd.log', 'a', 20000000, 10)
#logfile_handler.setFormatter(timestamp_formatter)
#logfile_handler.setLevel(logging.INFO)
#log.addHandler(logfile_handler)
#log.setLevel(logging.INFO)

class a52sd(Daemon):
	"""
	The A52 Statistics Daemon.

	This daemon is used to take periodic stats on:
	- the separate network interfaces on the flames
	- the SAN volumes' read / write load
	- SAN disk usage 
	- concurrent user load on the SANS
	
	It can also send email reports at specific times
	on certain stats 
	"""
	DEFAULTS = {'hosts':socket.gethostname(),
			'interval':'60s',
			'start':None,
			'days':['M','Tu','W','Th','F']} 

	def __init__(self,pidfile=None):
		log.info("Initializing A52 Stat Daemon")
		if pidfile:
			#Daemon.__init__(self,pidfile,stdout=self.logfile,stderr=self.logfile)
			Daemon.__init__(self,pidfile,logger=log)
		self.hostname = socket.gethostname()
		self.RPM = settings.RPM
		# validate the modules
		self.validate_modules(settings.modules)
	
	def validate_modules(self,modules):
		"""
		Validate each of the modules.
		Invalid modules will be removed so that valid ones can still function.
		Defaults for missing attributes are also added.
		"""
		self.modules = {}	
		for i,info in modules.iteritems():
			log.info("Checking module: %s" % i)
			valid = True
			if not info.has_key('method'):
				log.error("ERROR: Module (%s) Missing attribute: 'method'" % i)
				valid = False
			elif not type(info['method']).__name__ == 'classobj':
				log.error("ERROR: Module's 'method' attribute is not a classobj: %s" % info['method'])
				valid = False
			if info.has_key('hosts'):
				if not info['hosts']:
					info['hosts'] = self.DEFAULTS['hosts']
			if info.has_key('interval'):
				if type(info['interval']) is int:
					info['interval'] = "%ss" % info['interval']
				if not info['interval']:
					info['interval'] = self.DEFAULTS['interval']
			if info.has_key('start'):
				if not info['start']:
					info['start'] = self.DEFAULTS['start']
			if info.has_key('days'):
				if not info['days']:
					info['days'] = self.DEFAULTS['days']
			for attr in ['hosts','interval','start','days']:
				if not info.has_key(attr):
					info[attr] = self.DEFAULTS[attr]
			if valid:
				if self.hostname in info['hosts']:
					# add the next_marker attribute 
					info['next_marker'] = None
					# attach a scheduler 
					info['scheduler'] = scheduler(interval=info['interval'],
										start=info['start'],
										days=info['days'])
					self.modules[i] = info

	def __getattr__(self,name):
		if name == 'marker':
			self.marker = int(time.time())
			return self.marker
		message = "'%s' object has no attribute '%s'" % (__name__,name)
		raise AttributeError,message

	def run(self):
		"""
		This method is spawned from the Daemon.start() method
		"""
		log.info("Starting A52 Stat Daemon")
		while True:
			for i,info in self.modules.iteritems():
				log.info("Checking module: %s" % i)
				if info['scheduler'].g2g():
					if type(info['method']).__name__ == 'classobj':
						log.info("Running method: %s" % info['method'])
						module = info['method']()
						module.verbose = True
						try:
							module.run()
						#except Exception as e:
						except Exception,e:
							log.error("Module Error: %s" % info['method'])
							log.error(str(e))
							traceback.print_exc()
					log.info("Advancing module's scheduler: %s" % i)
					info['scheduler'].advance()
			time.sleep(self.RPM)



if __name__ == '__main__':
	# start/stop/restart the daemon
	if len(sys.argv) > 1:
		daemon = a52sd('/var/run/a52sd.pid')
		if sys.argv[1] == 'start':
			log.info("Starting daemon")
			daemon.start()
		elif sys.argv[1] == 'stop':
			log.info("Stopping daemon")
			daemon.stop()
		elif sys.argv[1] == 'restart':
			log.info("Restarting daemon")
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		log.info("Running a52sd directly")
		d = a52sd()
		d.run()



