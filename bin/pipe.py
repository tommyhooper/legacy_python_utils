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


class ffmpeg(threading.Thread):

	def __init__(self,command,encoder=None):
		self.command = command
		self.encoder = encoder
		threading.Thread.__init__(self)

	def run(self):
		self.job = popen2.Popen4(self.command,0)
		while self.job.poll() == -1:
			# capture the output of the command
			# for this command it's not necessary
			# to show the output
			sel = Select.select([self.job.fromchild], [], [], 0.05)
			if self.job.fromchild in sel[0]:
				output = os.read(self.job.fromchild.fileno(), 16384),
				print "%s\r" % output[0],
				sys.stdout.flush()
			#if self._stopped:
			#	os.kill(self.job.pid,signal.SIGTERM)
			#	break
			time.sleep(0.01)

		# mark that we're no longer running
		self.running = False
		# flush any possible info stuck in the buffer
		output = os.read(self.job.fromchild.fileno(), 16384)
		try:
			print output[0],
			sys.stdout.flush()
		except:pass
		print "\n"
		if self.job.poll():
			pass
			# got an error status bac
			#print "\n>>> Caught Error: %s\n" % self.job.poll()
		else:
			pass
			# inferno exited normally
			#print "\n>>> Normal Exit: %s\n" % self.job.poll()


def convert(infile,start,end,threads,slate=False):
	"""
	Process the convert command one frame
	at a time and write to the ffmpeg thread.

	Slate range: 240-433
	"""
	# prevent imagemagick from threading as 
	# it actually slows us down for this type
	# of operation (speed increase is roughly 2x)
	os.putenv('MAGICK_THREAD_LIMIT','1')
	count = end-start+1
	for i in range(start,end+1,1):
		target = infile % i
		if slate and (240 < i <= 433):
			for thread in threads:
				command = get_hoc_convert(target,encoder=thread.encoder)
				#print "\nCOMMAND:%s\n%s\n" % (i,command)
				status,data = commands.getstatusoutput(command)
				thread.job.tochild.write(data)
		else:
			command = get_hoc_convert(target)
			status,data = commands.getstatusoutput(command)
			for thread in threads:
				thread.job.tochild.write(data)


if __name__ == '__main__':
	pass








