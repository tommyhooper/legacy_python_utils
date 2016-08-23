""" A52 Module """

__version__ = "$Revision: 1.13 $".split()[-2:][0]

# setup logging for the A52 module
import os
import sys
import logging
import logging.config
path = os.path.dirname(os.path.abspath(__file__))
logging.config.fileConfig("%s/%s" % (path,'logging.ini'))


class Log:


	def __init__(self):
		pass

	def create_log(logfile,logdir="/var/log"):
		print "Creating log: %s/%s" % (logdir,logfile)
		# Create the log directory
		if not os.path.exists(logdir):
			os.makedirs(logdir)
			os.chmod(logdir, 0755)
	
		# Create the logger
		_log = Log()
		log = logging.getLogger(logfile)
		log.addHandler(_log.file_handler(logdir,logfile))
		log.addHandler(_log.stream_handler())
		log.setLevel(logging.DEBUG)
		return log
	create_log = staticmethod(create_log)

	def file_handler(self,logdir,logfile):
		# File handler
		# Keep 10 log files in the folder.
		log_handler = logging.handlers.RotatingFileHandler("%s/%s" % (logdir,logfile), 'a', 20000000, 10)
		#log_format = logging.Formatter('[%(asctime)s] %(lineno)s %(message)s','%b %d %H:%M:%S')
		log_format = logging.Formatter('[%(asctime)s] %(message)s','%b %d %H:%M:%S')
		log_handler.setFormatter(log_format)
		log_handler.setLevel(logging.INFO)
		return log_handler
		# Check if we need to rotate the log file
		#if os.path.exists(logfile):
		#	fhand.doRollover()
		#os.chmod(logFile, 0666)

	def stream_handler(self):
		# Stream handler
		stream_handler = logging.StreamHandler(sys.stdout)
		stream_format = logging.Formatter('%(message)s')
		stream_handler.setFormatter(stream_format)
		stream_handler.setLevel(logging.ERROR)
		return stream_handler
		#if os.getenv("DL_INSTALL_DEBUG"):
		#	stream_handler.setLevel(logging.DEBUG)
		#else:
		#	stream_handler.setLevel(logging.INFO)
	
	def create_rsync_log(logfile,logdir="/tmp"):
		# Create the log directory
		if not os.path.exists(logdir):
			os.makedirs(logdir)
			os.chmod(logdir, 0755)
	
		# Create the logger
		rsync_log = logging.getLogger('DL_MIRROR_RSYNC')
	
		# File handler
		# Keep 10 log files in the folder.
		rsync_log.abs_logfile = "%s/%s" % (logdir,logfile)
		log_handler = logging.handlers.RotatingFileHandler("%s/%s" % (logdir,logfile), 'a', 500000, 10)
		log_format = logging.Formatter('[%(asctime)s] %(message)s','%b %d %H:%M:%S')
		log_handler.setFormatter(log_format)
		rsync_log.addHandler(log_handler)
	
		log_handler.setLevel(logging.INFO)
		rsync_log.setLevel(logging.INFO)
		return rsync_log
	create_rsync_log = staticmethod(create_rsync_log)
	
