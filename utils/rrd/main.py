#!/usr/bin/env python

import os
import commands
import logging
log = logging.getLogger(__name__)


class rrd:
	"""
	A class for storing Round Robin Data
	"""

	def __init__(self):
		pass

	def update_rrd(self,rrd_file,timestamp,value,verbose=False):
		command = "rrdtool update %s %s:%s" % (rrd_file,timestamp,value)
		log.info(command)
		if verbose:
			print "  UPDATE:",command
		_err,_out = commands.getstatusoutput(command)
		if _err:
			log.error(_err)
			raise Exception,_err
		if verbose and _out:
			print "OUTPUT:",_out

	def lastupdate(self,rrd_file):
		"""
		Get the lastupdate timestamp
		"""
		command = "rrdtool lastupdate %s" % (rrd_file)
		output = commands.getoutput(command)
		for line in output.split('\n'):
			split = line.split(":")
			if len(split) > 1:
				return split[0]
		return None


if __name__ == '__main__':
	pass



