#!/usr/bin/python

import time
from datetime import *
import sys
import os
sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.Framestore import Framestore
from A52.dlProject import dlProject
from A52.dlLibrary import dlLibrary
from A52.dlProject_stats import dlProject_stats
from A52.utils import numberutil
from A52.utils import diskutil
from A52.utils import print_array
from A52.utils import messenger

#from optparse import OptionParser
#p = OptionParser()
#options,args = p.parse_args()


if __name__ == '__main__':
	base_path = '/hosts/meta01/Volumes'
	to_addrs = 'tommy.hooper@a52.com'
	#to_addrs = ['eng@a52.com','kevins@rockpaperscissors.com','josephr@a52.com','msousa@a52.com','danellis@a52.com','gabes@a52.com']
	from_addr = 'eng@a52.com'
	minute = datetime.today().minute
	hour = datetime.today().hour

	#hour = 2
	#minute = 0
	#if hour >= 2 and hour <= 6:
	#	sys.exit()

	intervals=[]
	# figure out what intervals we're good for
	if minute > 55 and hour in [1,5,9,13,15]:
		intervals.append('4h')
	elif minute < 5 and hour in [2,6,10,14,16]:
		intervals.append('4h')

	if minute > 55 or minute < 5:
		intervals.append('1h')
		intervals.append('30m')
		intervals.append('15m')

	if minute > 25 and minute <35:
		intervals.append('30m')
		intervals.append('15m')

	if minute > 10 and minute <20:
		intervals.append('15m')


	today = datetime.now()
	stones = Framestore.find(status='active')
	for fs in stones:
		path = "%s/%s" % (base_path,fs.data['mount_name'])
		df = diskutil.df(path)
		if df:
			used = int(round((df['bytes_used'] / (df['bytes_total'] *1.0))*100,0))
			subject = '%s @ %s%%' % (fs.data['name'],used)
			msg = None
			# we're assuming this process is run every 30 minutes
			if used >= 95 and '30m' in intervals:
				#print "%s at %s%% Send every 30 minutes" % (fs.data['name'],used)
				msg = "30 Minute Warning\n"
			elif used >= 90 and '1h' in intervals:
				#print "%s at %s%% Send every hour" % (fs.data['name'],used)
				msg = "1 Hour Warning\n"
			elif used >= 80 and '4h' in intervals:
				#print "%s at %s%% Send every 4 hours" % (fs.data['name'],used)
				msg = "4 Hour Warning\n"


		
			if msg:
				msg += "\n%10s: %s" % ('Free',numberutil.humanize(df['bytes_free'],scale='kilobytes'))
				msg += "\n%10s: %s" % ('Size',numberutil.humanize(df['bytes_total'],scale='kilobytes'))
				msg += "\n"
				msg += "\n%10s: %s" % ('Stone',fs.data['name'])
				msg += "\n%10s: %s" % ('Host',fs.data['host'])
				msg += "\n%10s: %s" % ('Volume',fs.data['volume'])
				msg += "\n%10s: %s\n" % ('Mount',fs.data['mount_name'])
	
				# get the project stats from the db
				# we want as close to an actual list of projects
				# on a framestore as possible without having to
				# either poll the wiretap server or browse through
				# the host's /usr/discreet/clip/stonefs directory
				# the closest thing to that list that we have is in 
				# the dl_libraries table.
				fs.du(source='db')
				msg += "%-15s%-15s%-15s%-30s\n" % ('Size (unique)','Size (shared)','Size (total)','Project')
				msg += "%s\n" % ("-"*90)
				for project in sorted(fs.pstats):
					info = fs.pstats[project]
					if info.data['poll_date'] and\
					   today - info.data['poll_date'] > timedelta(days=1):
						project = "[out of date] %s" % project
					msg += "%-15s%-15s%-15s%-30s\n" % (	info.dsp_bytes_self,
											info.dsp_bytes_shared,
											info.dsp_bytes_total,
											project)

				msg += "%s\n" % ("-"*90)
				msg += "%-15s%-15s%-15s%-30s\n" % (	fs.pstat_totals['dsp_bytes_self'],
										fs.pstat_totals['dsp_bytes_shared'],
										fs.pstat_totals['dsp_bytes_total'],
										'TOTAL')

				print msg
				#messenger.Email(from_addr,to_addrs,subject,msg)
				
