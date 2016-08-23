#!/usr/bin/python

import threading
import os
import commands
import Queue
import time
import sys
import datetime
import popen2 # Deprecated ./fuse_2011.py:5: DeprecationWarning: The popen2 module is deprecated.  Use the subprocess module.
import select as Select

from optparse import OptionParser
p = OptionParser()
#p.add_option("-a",dest='audiofile', type='string',help="audio file")
#p.add_option("-o",dest='outfile', default='hoc.mov',type='string',help="name of output file")
#p.add_option("-e",dest='encoder', default='both',type='string',help="encoder type: h264 or prores (default = both)")
#p.add_option("-t",dest='thread_num', default=2,type='int',help="number of threads to use for encoding (default:2)")
options,args = p.parse_args()

def help():
	print "\n usage: %s infile start end\n" % (os.path.split(sys.argv[0])[1])

def convert(command):
	"""
	Run the ffmpeg process and stream the output to the shell
	"""
	job = popen2.Popen4(command,0)
	while job.poll() == -1:
		# capture the output of the command
		# for this command it's not necessary
		# to show the output
		sel = Select.select([job.fromchild], [], [], 0.05)
		if job.fromchild in sel[0]:
			output = os.read(job.fromchild.fileno(), 16384),
			print "%s\r" % output[0],
			sys.stdout.flush()
		time.sleep(0.01)

	# flush any possible info stuck in the buffer
	output = os.read(job.fromchild.fileno(), 16384)
	try:
		print output[0],
		sys.stdout.flush()
	except:pass
	print "\n"
	if job.poll():
		pass
		# got an error status bac
		#print "\n>>> Caught Error: %s\n" % job.poll()
	else:
		pass
		# inferno exited normally
		#print "\n>>> Normal Exit: %s\n" % job.poll()


if __name__ == '__main__':

	infile = args[0]
	outfile = args[1]
	start = int(args[2])
	end = int(args[3])

	cmd_header = """ convert -verbose -resize 1920x960 -bordercolor "#000000" -border x60 """ 
	# 2050x1025/cntr_ex.*.dpx 1920x1080c/hd_ltrbx.%07d.dpx
	start_time = datetime.datetime.now()
#	for i in range (start,end+1,1):
#		_in = infile % i
#		_out = outfile % i
#		command = "%s %s %s" % (cmd_header,_in,_out)
#		print command
#		output = commands.getoutput(command)

	for i in range (start,end,201):
		if i > end:
			i = end
		in_seq = "%s[%d-%d]" % (infile,i,i+200)
		command = "%s %s %s" % (cmd_header,in_seq,outfile)
		print command
		output = commands.getoutput(command)
#		convert(command)

	if i < end:
		in_seq = "%s[%d-%d]" % (infile,i,end)
		command = "%s %s %s" % (cmd_header,in_seq,outfile)
		output = commands.getoutput(command)
#		convert(command)

	
	stop_time = datetime.datetime.now()
	delta = stop_time - start_time
	print "[41mSTOP[m: %s elapsed" % (delta)

