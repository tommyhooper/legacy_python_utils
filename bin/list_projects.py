#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import time
import datetime
import sys
import string
import os
import glob
import re
import commands




class Framestore:
	"""
	Simple class to query wiretap servers on hosts to
	get framestore volumes and project lists

	Note: uses precompiled wiretap utilities instead of the 
	wiretap API. 
	"""

	GET_CHILDREN = '/usr/discreet/wiretap/tools/current/wiretap_get_children'


	def __init__(self,hostname,name,nodeId,version):
		"""
		Framestore Object
		"""
		self.hostname = hostname
		self.name = name
		self.nodeId = nodeId
		self.version = version

	@staticmethod
	def get_stones(hostname):
		"""
		Get the stonefs nodes listed by the wiretap server.
		NOTE: not all nodes will be valid.
		"""
		stones = []
		version = None
		cmd = '%s -h %s -n /' % (Framestore.GET_CHILDREN,hostname)
		status,output = commands.getstatusoutput(cmd)
		if status == 0:
			for line in output.split('\n'):
				if 'stonefs' in line:
					version = 2014
					name = line.strip('/')
					stones.append(Framestore(hostname,name,line,version))
		if stones:
			return stones

		# 2015 wiretap has a different hierarchy
		cmd = '%s -h %s -n /volumes' % (Framestore.GET_CHILDREN,hostname)
		status,output = commands.getstatusoutput(cmd)
		if status == 0:
			for line in output.split('\n'):
				if 'stonefs' in line:
					version = 2015
					name = os.path.split(line)[1]
					stones.append(Framestore(hostname,name,line,version))
		return stones

	def list_projects(self):
		"""
		List the projects on the framestore
		"""
		self.projects = []
		cmd = '%s -h %s -n %s' % (Framestore.GET_CHILDREN,self.hostname,self.nodeId)
		status,output = commands.getstatusoutput(cmd)
		if status == 0:
			for line in output.split('\n'):
				if os.path.split(line)[1] != 'users':
					self.projects.append(os.path.split(line)[1])
		return self.projects




if __name__ == '__main__':
	from optparse import OptionParser
	p = OptionParser()
	p.add_option('-f', dest='hide_fake_projects', action='store_true',default=False,help='Hide fake projects (non job# projects)')
	options,args = p.parse_args()

	if not args:
		args = ['master01','master02','master03']

	print "Listing projects on:",', '.join(args)
	projects = {}
	for host in args:
		print "[44m%s[m" % host
		stones = Framestore.get_stones(host)
		
		for obj in stones:
			real_projects = []
			fake_projects = []
			print "\t[40m  ----------- %s ----------- [m" % obj.name
			for proj in obj.list_projects():
				regx = re.search("(^.*)([0-9]{2,2}[A-Z][0-9]{3,3})(.*)",proj)
				if regx:
					real_projects.append(proj)
				else:
					fake_projects.append(proj)

			real_projects.sort()
			fake_projects.sort()
			i = 1
			if real_projects:
				for proj in real_projects:
					print "\t%2d %s" % (i,proj)
					i+=1
			if fake_projects and not options.hide_fake_projects:
				#print "\t[41mUnrecognized projects:[m" 
				for proj in fake_projects:
					print "\t[31m%2d %s[m" % (i,proj)
					i+=1

