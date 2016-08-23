#!/usr/bin/python

import sys
import glob
import os
#from watchdog import watchdogDecorator
path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
	print "loading dev path..."
	to_addrs = 'tommy.hooper@a52.com'
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
	to_addrs = 'tina@a52.com'
from A52.utils.rsync import Rsync
from optparse import OptionParser
p = OptionParser()
p.add_option("-s",dest='source', type='string',help="source directory")
p.add_option("-d",dest='destination', type='string',help="destination directory")
p.add_option("-D",dest='delete', action='store_true',default=False,help="--delete mode")
p.add_option("-n",dest='dry_run', action='store_true',default=False,help="dry run")
p.add_option("-v",dest='verbose', action='store_true',default=False,help="verbose")
options,args = p.parse_args()
source = options.source
destination = options.destination
delete = options.delete
verbose = options.verbose

#@watchdogDecorator('rsync_loop')
def main():
	if not source or not destination:
	   p.print_help()
	   sys.exit()

	# check for the existence of source and destination
	if not os.path.exists(source):
	   print "ERROR: Could not find source: %s" % source
	   sys.exit()
	if not os.path.exists(destination):
	   print "ERROR: Could not find source: %s" % destination
	   sys.exit()

	# for the target directories which are 
	# all the directories directly below 'source'

	targets = glob.glob("%s/*" % source)
	i = 1
	for target in targets:
	   message = "Rsync %s of %s: %s" % (i,len(targets),target)
	   print message
	   logfile = "/tmp/rsync_%s.log" % os.path.basename(source)
	   rs = Rsync(source=target,destination=destination,dry_run=False,log_message=message,logfile=logfile,delete=delete,verbose=verbose)
	   rs.rsync()
	   i+=1

if __name__ == '__main__':
	main()
