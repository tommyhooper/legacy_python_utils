#!/usr/bin/env python

import os,commands

def df(mount):
	"""
	Parses the output of 'df for 'mount'
	and returns a dict
	"""
	if not os.path.exists(mount):
		print "ERROR (df): Could not find %s" % mount
		return None
	df = commands.getoutput('df -k %s' % mount).split()
	if df[0] == 'Filesystem':
		free = {
				'filesystem':df[7],
				'bytes_total':int(df[8]),
				'bytes_used':int(df[9]),
				'bytes_free':int(df[10]),
				'percent_used':df[11],
				'mount_point':df[12]}
		return free

if __name__ == '__main__':
	df('/usr')
