#!/usr/bin/env python

import os
import commands

def sw_wiretapd():
	"""
	Check to see if the wiretap server
	is running and if not run sw_start
	"""
	sw_start = '/usr/discreet/sw/sw_start'
	
	# we dont' want this cron to step on 
	# the boot up junk that happens so 
	# wait till we see the sw_probed
	probe_cmd = 'ps -C sw_probed -o pid='
	probe_pid = commands.getoutput(probe_cmd)
	if not probe_pid:
		return
	print "sw_probed: %s" % probe_pid

	# check for the sw_serverd
	sws_cmd = 'ps -C sw_serverd -o pid='
	sws_pid = commands.getoutput(sws_cmd)
	if not sws_pid:
		print commands.getoutput(sw_start)
		return
	print "sw_serverd: %s" % sws_pid

	# check for the sw_wiretapd
	wtd_cmd = 'ps -C sw_wiretapd -o pid='
	wtd_pid = commands.getoutput(wtd_cmd)
	if not wtd_pid:
		print commands.getoutput(sw_start)
		return
	print "sw_wiretapd: %s" % wtd_pid

	# check for the ifffsWiretapServer
	iffs_cmd = 'ps -C ifffsWiretapServer -o pid='
	iffs_pid = commands.getoutput(iffs_cmd)
	if not iffs_pid:
		print commands.getoutput(sw_start)
		return
	print "ifffsWiretapServer: %s" % iffs_pid
	

if __name__ == '__main__':
	sw_wiretapd()
