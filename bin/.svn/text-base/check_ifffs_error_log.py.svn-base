#!/usr/bin/python

#
#	CHECK IFFFS ERROR LOG
#
#	Simple nagios plugin to 
#	check if the ifffs_error.log
#	is getting too large. 
#	At 2MB the log prevents 
#	the flame from running.
#
#	Exit codes:
#	0	'OK'
#	1	'WARNING'
#	2	'CRITICAL'
#	3	'UNKNOWN'
#

import sys
import os

logfile = '/usr/discreet/log/ifffs_error.log'

if not os.path.exists(logfile):
	print "CHECK_IFFFS_ERROR_LOG CRITICAL: Could not find logfile"
	sys.exit(2)

try:
	stats = os.stat(logfile)
	size = stats.st_size
except:
	print "CHECK_IFFFS_ERROR_LOG CRITICAL: Could not stat logfile"
	sys.exit(2)

if size > 1000000:
	print "CHECK_IFFFS_ERROR_LOG WARNING: Log file size: %s" % size
	sys.exit(1)
if size > 1500000:
	print "CHECK_IFFFS_ERROR_LOG CRITICAL: Log file size: %s" % size
	sys.exit(2)

print "CHECK_IFFFS_ERROR_LOG OK: Log file size: %s" % size
sys.exit(0)

