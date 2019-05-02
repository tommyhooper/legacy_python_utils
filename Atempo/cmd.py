

import os
import re
import sys
import datetime
import commands
import select as Select
import time
import subprocess
import threading
import shlex
import tempfile

import logging
log = logging.getLogger('atempo_local')


class Command(object):
	"""
	Base object for running a command
	"""


	def __init__(self,command,check=False,verbose=False,print_line=None,pipe_stderr=True):
		"""
		check - if True command will not be run but printed instead (dry run)
		"""
		self.command = command
		self.check = check
		self.verbose = verbose
		self.print_line = print_line
		self.pipe_stderr = pipe_stderr
		self.status = None
		self.output = None
		self.stderr = None
		self.error = None
		self.error_code = 0

	def run(self):
		"""
		spawn the command 
		"""
		if self.print_line:
			log.info("%s..." % self.print_line)

		if self.check:
			log.info("[44mCMD[m: Dry run: %s" % self.command)
			self.status = True
			self.error = None
			return True

		self._run_subprocess()

	def _run_subprocess(self):
		if self.pipe_stderr:
			self.process = subprocess.Popen(shlex.split(self.command), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		else:
			self.stderr = []
			stderr = tempfile.TemporaryFile()
			self.process = subprocess.Popen(shlex.split(self.command), stdout=subprocess.PIPE, stderr=stderr)
		self.output = []
		lb = LineBuffer(verbose=self.verbose)
		while True:
			c = self.process.stdout.read(1)
			lb.add(c)
			if self.process.poll() != None:
				# read the rest of the buffer
				c = self.process.stdout.read()
				lb.add(c)
				break
		self.output = lb.output
		self.error_code = self.process.poll()
		if self.error_code == 0:
			return True
		# error, read the error from the tempfile
		if not self.pipe_stderr:
			stderr.seek(0)
			for line in stderr.readlines():
				self.stderr.append(line.strip('\n'))
			stderr.close()
		return False


class LineBuffer:
	"""
	Simple line buffer that gathers
	data and dumps complete lines to 
	the log and to stdout
	"""

	def __init__(self,verbose=False):
		self.data = ''
		self.verbose = verbose
		self.output = []
	
	def add(self,data):
		if self.verbose:
			sys.stdout.write(data)
			sys.stdout.flush()
		self.data+=data
		split = self.data.split('\n')
		if len(split) == 1:
			return
		# new line exists - write the lines
		# to the log and to stdout then clear self.data.
		# If the last character of self.data is a newline 
		# then we omit the empty last list item
		for line in split[:-1]:
			log.info(line)
			self.output.append(line)
		if split[-1] != '':
			log.info(line)
			self.output.append(line)
		self.data = ''
		
		

if __name__ == '__main__':
	#obj = Command('/tmp/tmpz8pXUG/flame_2014.0.3_LINUX64_RHEL5/INSTALL_FLAME --noui')
	obj = Command('who',verbose=True)
	obj.run()

