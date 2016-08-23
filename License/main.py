
import re
import socket
import commands
import os
import time
import traceback
from datetime import datetime
from datetime import timedelta
#from paramiko import *
#from settings import *
from A52.utils import print_array
from A52.utils import messenger 

import logging
log = logging.getLogger(__name__)



class ssh:

	
	def __init__(self):
		pass

	def ssh(self,host,command,username=False):
		if not username:
			username = os.getenv("USER")
		ssh = SSHClient()
		ssh.load_system_host_keys()
		ssh.connect(host,username='root')
		_in,_out,_err = ssh.exec_command(command)
		stdout = _out.readlines()
		stderr = _err.readlines()
		return (stdout,stderr)


class Server:


	def __init__(self,host,port):
		self.host=host
		self.port=port
		self.type = None
		self.version = None
		self.license_files = None
		self.daemons=[]

	def __iter__(self,*args):
		"""
		Iterate over the daemons
		and the daemon's features
		stored in this object
		"""
		for daemon in self.daemons:
			for feature in daemon.features:
				yield (daemon,feature)

	def add_daemon(self,daemon):
		self.daemons.append(daemon)

	def list_daemons(self):
		for d in self.daemons:
			d.info()

	def info(self):
		print "Server info:"
		print "\tStatus: %s" % self.status
		print "\tType: %s" % self.type
		print "\tHost: %s" % self.host
		print "\tPort: %s" % self.port
		print "\tVersion: %s" % self.version
		print "\tLicense Files (server): %s" % self.license_files
		print "\t# of Daemons: %s" % len(self.daemons)


class Daemon:


	def __init__(self,server):
		self.server = server
		self.features = []

	def __iter__(self,*args):
		"""
		Iterate over the features
		and the feature's users
		stored in this object
		"""
		for feature in self.features:
			for user in feature.users:
				yield (feature,user)

	def add_feature(self,feature):
		self.features.append(feature)

	def list_features(self):
		for f in self.features:
			f.info()
		
	def info(self):
		print "Daemon: %s" % self.name
		print "\tStatus: %s" % self.status
		print "\tVersion: %s" % self.version
		print "\t# of Features: %s" % len(self.features)

class Feature:
	

	def __init__(self,daemon,name='unknown',f_type=None,version=None,vendor=None,total=0,in_use=0):
		self.daemon = daemon
		self.name=name,
		self.type=f_type
		self.version=version
		self.vendor=vendor
		self.total=total
		self.in_use=in_use
		self.users = []

	def __iter__(self,*args):
		"""
		Iterate over the users
		stored in this object
		"""
		for user in self.users:
			yield user

	def add_user(self,user):
		self.users.append(user)

	def list_users(self):
		for u in self.users:
			u.info()

	def info(self):
		print "Feature: %s" % self.name
		print "\tType: %s" % self.type
		print "\tVendor: %s" % self.vendor
		print "\tVersion: %s" % self.version
		print "\tTotal Licenses: %s" % self.total
		print "\tTotal In use: %s" % self.in_use
		

class User:
	

	def __init__(self,feature,**kwargs):
		self.feature = feature
		self.__dict__.update(kwargs)

	def remove(self):
		log.info("Removing user %s" % self.user)
		feature = self.feature
		daemon = feature.daemon
		server = daemon.server
		lmutil.lmremove(feature.name,server,server.port,user.id_num)

	def info(self):
		print "User: %s:" % self.user
		print "\tHost: %s" % self.host1
		print "\tHost(2): %s" % self.host2
		print "\tVersion: %s" % self.version
		print "\tStart time: %s" % " ".join(self.start_time)
		print "\tCheckout ID: %s" % self.id_num



if __name__ == '__main__':
	pass





