#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import time
import datetime
import sys
import string
import ldap
import socket
from A52.utils import print_array

class ActiveDirectoryError(Exception):
	pass

class ActiveDirectoryBindError(Exception):
	pass

class ActiveDirectoryAccountError(Exception):
	pass

class AuthenticationError(Exception):
	pass

class AD:

	"""
	Authentication class for Active Directory

	
		server = ldap.initialize("ldap://a52dc01")
		server.simple_bind_s("rush","area52")
		server.set_option(ldap.OPT_REFERRALS, 0)

		# user id: (staff / freelance)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_id)
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_id)

		# title: (staff / freelance)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"title=%s" % title)
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"title=%s" % title)

		# department: (staff / freelance)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"Department=%s" % department)
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"Department=%s" % department)

		# all:
		scope = staff | freelance
		result_id = server.search('ou=%s,ou=a52,dc=a52,dc=com' % scope,ldap.SCOPE_SUBTREE,"cn=*")

		# iterating through the results: 
		while 1:
			r_type, info = server.result(result_id, 0)
			if (info == []):
				break
			else:
				if r_type == 100:
					obj = User()
					user_id = info[0][1]['sAMAccountName'][0]
					obj.data = info[0][1]
					obj.user_id = user_id
					obj.cn = info[0][1]['cn'][0]
					obj.employment_status = 'staff'
					users.append(obj)

	"""

	def __init__(self):
		"""
		Active Directory Object
		"""
		pass

	#@staticmethod
	def authenticate(username,password,domain="a52.com"):
		"""
		Authenticate against the active directory server
		using 'username' and 'password'
		"""
		server = ldap.initialize("ldap://a52dc01")
		try:
			# in order to bind successfully we declare
			# the domain in the username. 
			# this can be done in one of two ways:
			#	username@domain    ...or...
			#	domain\username
			server.simple_bind_s("%s@%s" % (username,domain),password)
		except ldap.INVALID_CREDENTIALS:
			message = "Could not bind to active directory server"
			raise ActiveDirectoryBindError,message
		server.set_option(ldap.OPT_REFERRALS, 0)
		server.protocol_version = ldap.VERSION3
		base = 'ou=a52,dc=a52,dc=com'
		scope = ldap.SCOPE_SUBTREE
		_filter = "(&(objectClass=user)(sAMAccountName="+username+"))"
		attrs = ["department"]
		result_id = server.search(base, scope, _filter, attrs)
		_type, user = server.result(result_id,60)
		# User may have authenticated but not have an
		# account login name (sAMAccountName).
		# we still return True but print a warning message
		if not user:
			message = "User does not have a login id (sAMAccountName)"
			#raise ActiveDirectoryAccountError,message
			print message
			return True
		name,info = user[0]
		if info and info.has_key('department'):
			department = info['department']
		else:
			department = ['guest']
		return (name,department)
	authenticate = staticmethod(authenticate)


if __name__ == '__main__':
#	AD.authenticate('rush','area52')
#	AD.authenticate('root','xxx')
	AD.authenticate('tommy.hooper','xxx')
#	AD.authenticate('a52\\tommy.hooper','')
	pass



