#!/usr/bin/env python

import sys
sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
import re
import os
import socket
from models import dl_users
from A52.utils import print_array
from A52.utils import dbg 
from A52 import settings
from A52 import environment
from A52.Framestore import Framestore
from A52 import utils

CONTEXT = environment.get_context()

class dlUser(dl_users):

	DEFAULTS ={	'PreferenceDir':'',
			'category':'effects'}
	CHOICES = {	'category':['editing','effects']}

	def __init__(self,host,volume,user_name,**kwargs):
		"""
		DL Project Object
		"""
		self.host = host
		self.volume = volume
		self.user_name = user_name
		self.data = DEFAULTS
		self.data.update(kwargs)
		self.default = settings.DL_PROPERTIES[CONTEXT]

	def __getattr__(self,name):
		"""
		Catch specific attributes if they are
		used before they are set and set them here
		for convenience
		"""
		if name == 'version_short':
			version_short = self.get_version_short()
			if version_short:
				self.version_short = self.get_version_short()
				return self.version_short
		if name == 'localhost':
			hostname = socket.gethostname()
			if hostname:
				self.localhost = hostname
				return self.localhost
		if name == 'software':
			software = self.get_software()
			if software:
				self.software = software
				return self.software
		message = "'dlUser' object has no attribute '%s'" % name
		raise AttributeError,message

	def get_version_short(self):
		"""
		Return the year portion of the version
		"""
		if not self.data.has_key('version'):
			return 2011
		if self.data['version']:
			return re.search('^([0-9]{4}).*$',self.data['version']).group(1)
		return 2011
	
	def get_software(self):
		"""
		Return the software type based on the user category
		"""
		if not self.data.has_key('category'):
			return None
		if self.data['category'] == 'effects':
			return 'flame'
		elif self.data['category'] == 'editing':
			return 'smoke'
		return None
			
	def create_user_files(self):
		"""
		Check for the users directory and copy over 
		the template if the user is new
		"""
		# setup the rsync command for the user:
		template = '%s/%s/user/%s' % (self.default['template_dir'],self.version_short,self.software)
		user_dir = "%s/%s/%s/%s" % (self.default['user_setup_home'],self.version_short,self.data['name'],self.data['category'])
		if not os.access(user_dir,os.R_OK):
			print "makedirs(%s)" % user_dir
			utils.makedirs(user_dir)
		command = "rsync -a --ignore-existing %s/ %s/" % (template,user_dir)
		print "Rsyncing user template:",command
 		success = os.system(command)
		return

	def create_user_link(self):
		"""
		The flame seems to always look for users in /usr/discreet/user
		Let's create a link to the 'real' location
		"""
		# flame ignores the PreferenceDir attribute... have to create a link
		link_base = "/usr/discreet/user/%s" % (self.data['category'])
		#target = "%s/%s" % (link_base,self.data['name'])
		target = "/hosts/%s/%s/%s" % (self.data['host'],link_base,self.data['name'])
		# check if a user directory already exists
		if not os.path.islink(target) and os.path.isdir(target):
			print "WARNING: User directory exists. Replacing it with a link..."
			os.rename(target,target+'.local')
		# now create the link
		source = "%s/%s/%s/%s" % (self.default['user_setup_home'],self.version_short,self.data['name'],self.data['category'])
		print "utils.symlink(%s,%s)" % (source,target)
		utils.symlink(source,target)

	##
	## FROM MODELS
	##
	def _create_user(self):
		"""
		Check for this user on the framestore. Create a new user
		if one does not already exist.
		"""
		user = self.data['name']
		# check to see if this user exists or not
		if self.framestore.find_user(category=self.data['category'],user=user):
			# user already exists
			dbg("User %s exists" % (user))
			return 'Exists'
		else:
			dbg("User %s is new, creating..." % (user))
			# create the xml stream with the settings
			xmlstream ="<User>"
			xmlstream+="<Name>%s</Name>" % user
			#xmlstream+="<PreferenceDir>%s</PreferenceDir>" % (self.data['PreferenceDir'])
			xmlstream+="</User>"
			dbg("Creating user")
			dbg("XML: %s" % xmlstream)
			self.framestore.create_user(self.data['category'],user,xmlstream)
		return True



if __name__ == '__main__':
	#user = dlUser(name='tommy',category='effects',user_id='tommy')
	dl_user = dlUser(	host='smoke01',
				volume='stonefs4',
				category='effects',
				name='tommy',
				user_id='tommy')
#	dl_user.inspect()
	dl_user.create_user_link()
#	user.create()
#	user.inspect()
#	user = dlUser()
#	user.data['user_id'] = 'tommy'
#	user.data['name'] = 'wt_user07'
#	user.data['category'] = 'effects'
#	user.create_user_files()
#	user.create_user_link()
#	user.create()
	pass



