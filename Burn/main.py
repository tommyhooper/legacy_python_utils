#!/usr/bin/env python

#import glob
#import os
#import stat
#import sys
#import time
#import re
#import traceback
#import Queue
#import threading
#from datetime import datetime
#from wiretap import Wiretap
#from A52.utils import print_array
#from A52.utils import diskutil
#from A52.utils import numberutil
#from A52.utils import fileutil
#from A52.dlLibrary import dlLibrary
from job import BurnJob

#class FramestoreException(Exception):
#	pass

class Burn(object):
	"""
	Main class to manipulate Burn jobs
	"""

	def __init__(self,host,volume):
		# run the wiretap init
		#super(Framestore,self).__init__()
		self.host = host
		self.volume = volume
		self.locks = {}
		# stat objects for each project:
		self.pstats = {}
		self.pstat_totals = {
			'frames_self':0,
			'frames_shared':0,
			'frames_total':0,
			'bytes_self':0,
			'bytes_shared':0,
			'bytes_total':0,
			'dsp_bytes_self':'',
			'dsp_bytes_shared':'',
			'dsp_bytes_total':'',
		}
		# stat dictionaries for project groups
		self.pstat_groups = {}

	def __getattr__(self,name):
		if name == 'bytes_used':
			self.format_df()
			return self.bytes_used
		if name == 'bytes_free':
			self.format_df()
			return self.bytes_free
		if name == 'bytes_total':
			self.format_df()
			return self.bytes_total
		if name == 'dsp_bytes_used':
			self.format_df()
			return self.dsp_bytes_used
		if name == 'dsp_bytes_free':
			self.format_df()
			return self.dsp_bytes_free
		if name == 'dsp_bytes_total':
			self.format_df()
			return self.dsp_bytes_total
		if name == 'percent_used':
			self.format_df()
			return self.percent_used
		if name == 'fraction_used':
			self.format_df()
			return self.fraction_used
		return super(Framestore,self).__getattr__(name)
		message = "'%s' has no attribute %s" % (__name__,name)
		raise AttributeError,message
	



if __name__ == '__main__':

	j = BurnJob()
	j.parse_log()
