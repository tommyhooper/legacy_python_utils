#!/usr/bin/python

import time
import sys
import os
import glob

hosts = ['flame01','flame02','flame03','smoke01','smack01']

if len(sys.argv) == 1:
	print "usage: %s project [project]..." % sys.argv[0]
	sys.exit()

for project in sys.argv[1:]:
	print "\nSearching for %s..." % project
	for host in hosts:
		volumes = glob.glob('/hosts/%s/usr/discreet/clip/stonefs?' % host)
		for volume in volumes:
			ppath = "%s/%s" % (volume,project)
			if os.path.exists(ppath):
				print "\tFound project on %s/%s unlocking..." % (host,os.path.basename(volume))
				reflog = "%s/%s/.ref.log" % (volume,project)
				refrec = "%s/%s/.ref.rec" % (volume,project)
				print "\t\tRemoving %s" % reflog
				os.remove(reflog)
				print "\t\tRemoving %s" % refrec
				os.remove(refrec)

	

