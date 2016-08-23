#!/usr/bin/python

import time
from datetime import *
import sys
import socket
import os
path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	print "Loading dev path"
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
from A52.Framestore import Framestore
from A52.utils import numberutil
from A52 import environment
environment.set_context('live')


from optparse import OptionParser
p = OptionParser()
p.add_option("-f",dest='poll', action='store_true',default=False,help="Rescan each project for actual size. WARNING: This process can take a while as every frame in a project is scanned.")
p.add_option("-v",dest='verbose', action='store_true',default=False,help="Verbose output. Shows projects, libraries, and clips as they are gathered.")
options,args = p.parse_args()


if __name__ == '__main__':

	if len(args) == 0:
		print "\nusage: %s sanstone_name [project(s)]\n" % sys.argv[0]
		sys.exit()
		hostname = socket.gethostname()
		stones = Framestore.find(host=hostname,status='active')
	elif len(args) == 1:
		stones = Framestore.find(name=args[0],status='active')
		projects = None
	elif len(args) > 1:
		stones = Framestore.find(name=args[0],status='active')
		projects = args[1:]

	if not stones:
		print "Could not find framestore: %s" % sanstone
		print "Should be one of:"
		all_fs = Framestore.find(status='active')
		for fs in all_fs:
			print "\t",fs.data['name']
		sys.exit()

	today = datetime.now()
	for fs in stones:
		if options.poll:
			print "Getting project stats from the framestore (this may take a while)..."
			fs.du(source='fs',verbose=options.verbose)
		else:
			print "Getting project stats from the database..."
			fs.du(source='db')
		print "Calculating sizes for %s" % fs.data['name']
		print "%-15s%-15s%-15s%-30s" % ('Size (unique)','Size (shared)','Size (total)','Project')
		print "-"*90
		p_total = 0
		for project in sorted(fs.pstats):
			info = fs.pstats[project]
			if info.data['poll_date'] and\
			   today - info.data['poll_date'] > timedelta(days=1):
				project = '[out of date] %s' % project
			print "%-15s%-15s%-15s%-30s" % (	info.dsp_bytes_self,
									info.dsp_bytes_shared,
									info.dsp_bytes_total,
									project)

		print "-"*90
		print "%-15s%-15s%-15s%-30s" % (	fs.pstat_totals['dsp_bytes_self'],
								fs.pstat_totals['dsp_bytes_shared'],
								fs.pstat_totals['dsp_bytes_total'],
								'TOTAL')


