#!/usr/bin/env python

from models import mailing_lists
from A52.db import controller
from A52.utils import print_array
db = controller()

import datetime
import time
#import logging
import sys
import os
sys.path.insert(0,'/Volumes/discreet/dev/GAM')

# import GAM
#import sys, os, time, datetime, random, cgi, socket, urllib, csv, getpass, platform, re, webbrowser, pickle
#import xml.dom.minidom
#from sys import exit
import pickle
import platform
import gdata.apps.service
import gdata.apps.emailsettings.service
import gdata.apps.adminsettings.service
import gdata.apps.groups.service
import gdata.apps.audit.service
import gdata.apps.multidomain.service
import gdata.apps.orgs.service
import gdata.apps.res_cal.service
import gdata.auth
import atom
import gdata.contacts
import gdata.contacts.service
import gdata.auth
#from hashlib import sha1

__author__ = 'jay0lee@gmail.com (Jay Lee)'
__version__ = '2.1.3'
__license__ = 'Apache License 2.0 (http://www.apache.org/licenses/LICENSE-2.0)'

class MailingList(mailing_lists):

	possible_scopes = ['https://apps-apis.google.com/a/feeds/groups/',                      # Groups Provisioning API
                         'https://apps-apis.google.com/a/feeds/alias/',                       # Nickname Provisioning API
                         'https://apps-apis.google.com/a/feeds/policies/',                    # Organization Provisioning API
                         'https://apps-apis.google.com/a/feeds/user/',                        # Users Provisioning API
                         'https://apps-apis.google.com/a/feeds/emailsettings/2.0/',           # Email Settings API
                         'https://apps-apis.google.com/a/feeds/calendar/resource/',           # Calendar Resource API
                         'https://apps-apis.google.com/a/feeds/compliance/audit/',            # Audit API
                         'https://apps-apis.google.com/a/feeds/domain/',                      # Admin Settings API
                         'https://www.googleapis.com/auth/apps/reporting/audit.readonly',     # Admin Audit API
                         'https://www.googleapis.com/auth/apps.groups.settings',              # Group Settings API
                         'https://www.google.com/m8/feeds/profiles',                          # Profiles API
                         'https://www.google.com/calendar/feeds/',                            # Calendar Data API
                         'https://www.google.com/hosted/services/v1.0/reports/ReportingData'] # Reporting API

	def __init__(self,**kwargs):
		"""
		Project Object
		"""
		self.domain = 'a52.com'
		self.data = {}
		self.data.update(kwargs)

	def commonAppsObjInit(self,appsObj):
		#Identify GAM to Google's Servers
		appsObj.source = 'Google Apps Manager %s / %s / Python %s.%s.%s %s / %s %s /' % (__version__, __author__,
			sys.version_info[0], sys.version_info[1], sys.version_info[2],
			sys.version_info[3], platform.platform(), platform.machine())
		#Show debugging output if debug.gam exists
		if os.path.isfile(self.getGamPath()+'debug.gam'):
			appsObj.debug = True
		return appsObj

	def getGroupsObject(self):
		apps = self.getAppsObject()
		groupsObj = gdata.apps.groups.service.GroupsService()
		if not self.tryOAuth(groupsObj):
			groupsObj.domain = self.domain
			groupsObj.SetClientLoginToken(apps.current_token.get_token_string())
		groupsObj = self.commonAppsObjInit(groupsObj)
		return groupsObj

	def getGamPath(self):
		if os.path.abspath('/') != -1:
			divider = '/'
		else:
			divider = '\\'
		return os.path.dirname(os.path.realpath(sys.argv[0]))+divider

	def tryOAuth(self,gdataObject):
		if os.path.isfile(self.getGamPath()+'oauth.txt'):
			oauthfile = open(self.getGamPath()+'oauth.txt', 'r')
			self.domain = oauthfile.readline()[0:-1]
			token = pickle.load(oauthfile)
			oauthfile.close()
			gdataObject.domain = self.domain
			gdataObject.SetOAuthInputParameters(gdata.auth.OAuthSignatureMethod.HMAC_SHA1, consumer_key='707389840191.apps.googleusercontent.com', consumer_secret='m-hW_l24IhsaNXtbtIc6ABac')
			token.oauth_input_params = gdataObject._oauth_input_params
			gdataObject.SetOAuthToken(token)
			return True
		else:
			return False

	def getAppsObject(self):
		#First see if a auth token is stored in token.txt
		#path = os.path.dirname(os.path.abspath(sys.argv[0]))
		isValid = False
		apps = gdata.apps.service.AppsService()
		if self.tryOAuth(apps):
			isValid = True
		elif os.path.isfile(self.getGamPath()+'token.txt'):
			#See if our token is still valid
			tokenfile = open(self.getGamPath()+'token.txt', 'r')
			self.domain = tokenfile.readline()[0:-1]
			token = tokenfile.readline()
			tokenfile.close()
			apps.domain = self.domain
			apps.SetClientLoginToken(token)
			try:
				edition = apps.Get('/a/feeds/domain/2.0/%s/accountInformation/edition' % apps.domain)
				isValid = True
			except gdata.service.RequestError, e:
				if e.message['reason'] == 'Domain cannot use API':
					print 'The Provisioning API is not on for your domain, please see:'
					print '  http://code.google.com/p/google-apps-manager/wiki/GettingStarted'
					exit(1)
			except socket.error, e:
				print "\nERROR: Failed to connect to Google's servers.  Please make sure GAM is not being blocked by Firewall or Antivirus software"
				sys.exit(1)
		if not isValid:
			if os.path.isfile(self.getGamPath()+'auth.txt'):
				authfile = open(self.getGamPath()+'auth.txt', 'r')
				self.domain = authfile.readline()[0:-1]
				username = authfile.readline()[0:-1]
				passwd = authfile.readline()
			else:
				self.domain = raw_input('Google Apps Domain: ')
				username = raw_input('Google Apps Admin Username: ')
				passwd = getpass.getpass('Google Apps Admin Password: ')
			email = username+'@'+self.domain
			apps = gdata.apps.service.AppsService(email=email, domain=self.domain, password=passwd)
			try:
				apps.ProgrammaticLogin()
				testapps = apps.RetrieveUser(username)
			except gdata.service.BadAuthentication, e:
				print "\nERROR: Invalid username or password.  Please try again."
				sys.exit(1)
			except gdata.apps.service.AppsForYourDomainException, e:
				print "\nERROR: Either the user you entered is not a Google Apps Administrator or the Provisioning API is not enabled for your domain. Please see: http://www.google.com/support/a/bin/answer.py?hl=en&answer=60757"
				sys.exit(1)
			except socket.error, e:
				print "\nERROR: Failed to connect to Google's servers.  Please make sure GAM is not being blocked by Firewall or Antivirus software"
				sys.exit(1)
			tokenfile = open(self.getGamPath()+'token.txt', 'w')
			tokenfile.write(self.domain+"\n")
			tokenfile.write(apps.current_token.get_token_string())
			tokenfile.close()
		apps = self.commonAppsObjInit(apps)
		return apps

	def requestOAuth(self):
		client_key = 'anonymous'
		client_secret = 'anonymous'
		fetch_params = {'xoauth_displayname':'Google Apps Manager'}
		scopes = self.possible_scopes
		apps = gdata.apps.service.AppsService(domain=self.domain)
		apps = self.commonAppsObjInit(apps)
		apps.SetOAuthInputParameters(gdata.auth.OAuthSignatureMethod.HMAC_SHA1, consumer_key=client_key, consumer_secret=client_secret)
		request_token = apps.FetchOAuthRequestToken(scopes=scopes, extra_parameters=fetch_params)
		final_token = apps.UpgradeToOAuthAccessToken(request_token)
		oauth_filename = 'oauth.txt'
		f = open(self.getGamPath()+oauth_filename, 'w')
		f.write('%s\n' % (self.domain,))
		pickle.dump(final_token, f)
		f.close()

	def getOrgObject(self):
		apps = self.getAppsObject()
		orgObj = gdata.apps.orgs.service.OrganizationService()
		if not self.tryOAuth(orgObj):
			orgObj.domain = self.domain
			orgObj.SetClientLoginToken(apps.current_token.get_token_string())
		orgObj = self.commonAppsObjInit(orgObj)
		return orgObj


	#------------------------------------------------------------------------------------------------------------------
	def doPrintGroups(self):
		groupsObj = self.getGroupsObject()
		groupsObj.domain = self.domain
		all_groups = groupsObj.RetrieveAllGroups()
		for g in all_groups:
			print "G:",g

	def doGetGroupInfo(self,group_name):
		groupObj = self.getGroupsObject()
		group = groupObj.RetrieveGroup(group_name)
		print 'Group Name: ',group['groupName']
		try:
			print 'Email Permission: ',group['emailPermission']
		except KeyError:
			print 'Email Permission: Unknown'
		print 'Group ID: ',group['groupId']
		print 'Description: ',group['description']
		members = groupObj.RetrieveAllMembers(group_name)
		users = []
		for member in members:
			users.append(member['memberId'])
		for user in users:
			if groupObj.IsOwner(user, group_name):
				print 'Owner:',user
			else:
				print 'Member:',user

	def doPrintUsers(self):
		org = self.getOrgObject()
		all_users = org.RetrieveAllOrganizationUsers()
		for user in all_users:
			print "USER:",user
			#email = user['orgUserEmail']
			#domain = email[email.find('@')+1:]
		
	def gCreate(self):
		if group_permission.lower() == 'owner':
			group_permission = 'Owner'
		elif group_permission.lower() == 'member':
			group_permission = 'Member'
		elif group_permission.lower() == 'domain':
			group_permission = 'Domain'
		elif group_permission.lower() == 'anyone':
			group_permission = 'Anyone'
		groupObj = getGroupsObject()
		result = groupObj.CreateGroup(group, group_name, group_description, group_permission)

	def getDomains(self):
		pass
		

if __name__ == '__main__':
	m = MailingList()
	apps = m.getAppsObject()
	apps.domain='a52.com'
	for page in apps.GetGeneratorForAllUsers():
		for user in page.entry:
			print 'Email:',user.login.user_name
			print 'First:',user.name.given_name
			print 'Last:',user.name.family_name

			break
#			email = user.login.user_name.lower() + '@a52.com'
#			print "EMAIL:",email


#	m.doPrintGroups()
#	m.doGetGroupInfo('Producers')
#	m.doPrintUsers()
	pass








