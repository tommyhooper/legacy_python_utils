#!/usr/bin/python

#
#	CHECK MOUNT
#
#	Simple nagios plugin to 
#	check if a path is a 
#	mount point
#
#	Exit codes:
#	0	'OK'
#	1	'WARNING'
#	2	'CRITICAL'
#	3	'UNKNOWN'
#

import sys
import os

try:
	path = sys.argv[1]
except:
	print "usage: %s <mount_path>" % sys.argv[0]
	sys.exit(3)


if os.path.ismount(path):
	print "CHECKMOUNT OK: %s is a mounted volume." % (path)
	sys.exit(0)
else:
	print "CHECKMOUNT CRITICAL: %s is not a mounted volume." % (path)
	sys.exit(2)

