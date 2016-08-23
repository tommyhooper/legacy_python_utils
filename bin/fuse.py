
import os
import sys
import re
import socket
import logging
from logging import handlers
from optparse import OptionParser
p = OptionParser()

path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	sys.path.insert(0,'/Volumes/discreet/dev/python2.6/site-packages')
	print "loading dev path..."
	#to_addrs = 'tommy.hooper@a52.com'
else:
	sys.path.insert(0,'/Volumes/discreet/lib/python2.6/site-packages')
	#to_addrs = 'eng@a52.com'
from fuse_ui import FuseUi
from fuse import FuseUi

for p in sys.path:
	print " ",p

def main(argv=sys.argv):
	"""
	Parse args, setup logging, and run the main fuse_ui
	"""
	# create a log for the this module
	log = logging.getLogger('fuse')
	log.setLevel(logging.DEBUG)
	log_handler = handlers.RotatingFileHandler('/usr/discreet/log/fuse.log','a', 20000000, 50)
	log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
	log_handler.setFormatter(log_format)
	log.addHandler(log_handler)
	log.info('test set level')
	
	#parser = argparse.ArgumentParser()
	p.add_option('--width', dest='width', type=int, default=1920, help='Width of the window')
	p.add_option('--height', dest='height', type=int, default=1080, help='Height of the window')
	p.add_option('-v', dest='version', help='Version to use. e.g. flame_2012.1.SP4')
	p.add_option('-d', dest='debug', action='store_true',default=False,help='Turn on debugging')
	#args = parser.parse_args()
	options,args = p.parse_args()

	if not options.version:
		if os.uname()[0].lower() == 'darwin':
			iffsHome = 'smoke_2013.2.53'
		else:
			try:
				iffsHome = os.getenv('HOME')
			except:
				print 'Could not find HOME environment variable. Exiting...'
				sys.exit()
	else:
		iffsHome = options.version
	
	dlInfo = parseIffsHome(iffsHome)
	dlInfo['width'] = options.width
	dlInfo['height'] = options.height

#	log_level = None
#	if options.debug:
#		log_level = 'debug'
	FuseUi.run(dlInfo)

def parseIffsHome(iffsHome):
	"""
	Set variables related to what software / version we're running
	"""
	iffsHome = iffsHome.rstrip("/")
	dl = {'home': iffsHome}
	
	try:
		regx = re.search("([A-z].*)_([0-9]*)(.*)", os.path.basename(iffsHome))
		# use this to ignore the period between the major and minor versions
		#regx = re.search("([A-z].*)_([0-9]*)\.(.*)",options.version)
		dl['software'] = regx.group(1)
		dl['version_short'] = regx.group(2)
		if regx.group(3):
			dl['version'] = "%s%s" % (regx.group(2), regx.group(3))
			dl['subversion'] = regx.group(3)
		else:
			dl['version'] = "%s" % (regx.group(2))
			dl['subversion'] = None
	except:
		message = "Could not parse home directory: %s" % iffsHome
		raise Exception, message
	
	# if this is one of the 'premium' versions,
	# let's strip the word premium out of the name
	dl['software_short'] = dl['software'].replace('premium', '')
	
	# first set the HOME
	if dl['software'] == 'smoke' or dl['software'] == 'smokepremium' or dl['software'] == 'conform':
		dl['user_category'] = 'editing'
	else:
		dl['user_category'] = 'effects'
	
	if dl['home'][0] != '/':
		dl['home'] = "/usr/discreet/%s" % (dl['home'])
	
	dl['executable'] = "%s/bin/startApplication" % (dl['home'])
	
	if not os.access(dl['executable'], os.R_OK):
		message = "Could not find: (%(executable)s)." % (dl)
		log.error(message)
		#raise Exception, message
	
	dl['platform'] = os.uname()[0].lower()
	dl['machine_type'] = os.uname()[4]
	dl['host'] = socket.gethostname()
	dl['volume'] = None
	dl['exclude_hosts'] = []
	return dl

#if __name__ == '__main__':
#	main()
