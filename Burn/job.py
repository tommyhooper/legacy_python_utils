


class BurnJob(object):


	def __init__(self):
		self.logfile = '/tmp/burnlog.txt'
		pass


	def parse_log(self):
		"""
		Parse a log file for this burn job and
		split up relative information.
		"""
		logfile = open(self.logfile,'r')
		for newline in logfile.readlines():
			line = newline.strip('\n')
			if line[:5] == 'BATCH':
				print line
