#!/usr/bin/python
# version 1.0
# $Revision: 1.6 $

import time
import datetime
import sys
import string
import ldap
import socket
from A52.db.orm import Record
from A52.utils import print_array
from A52.vTree import vTree
from models import users
from fake_users import fake_users

class User(users):


	def __init__(self,**kwargs):
		"""
		User Object
		"""
		self.data = {}
		self.data.update(**kwargs)

	#@staticmethod
	def find(department=None,user_id=None,title=None):
		if department:
			users = User.find_by_department(department=department)
			fk_users = User().find_fake_users(department=department)
			for u in fk_users:
				users.append(u)
			return users
		if user_id:
			users = User.find_by_user_id(user_id=user_id)
			if not users:
				return User().find_fake_users(user_id=user_id)
				# see if we have a fake user with this user_id
			return users
		if title:
			users = User.find_by_title(title)
			fk_users = User().find_fake_users(title=title)
			for u in fk_users:
				users.append(u)
			return users
	find = staticmethod(find)

	def find_fake_users(self,department=None,user_id=None,title=None):
		"""
		Create a user object for each of the 
		fake users for 'department'
		"""
		fk_users = []
		if department:
			if fake_users.has_key(department):
				for fk_user in fake_users[department]:
					user = User()
					user.__dict__.update(fk_user)
					fk_users.append(user)
		if user_id:
			for fk_user in fake_users['all']:
				if fk_user['user_id'] == user_id:
					user = User()
					user.__dict__.update(fk_user)
					fk_users.append(user)
		if title:
			for fk_user in fake_users['all']:
				if fk_user['data']['title'] == title:
					user = User()
					user.__dict__.update(fk_user)
					fk_users.append(user)
		return fk_users

	#@staticmethod
	def find_by_user_id(user_id=None):
		"""
		Search Active Directory and return
		a User object for each result
		Note: for now the search is limited to
		department until I can accomodate the 
		more complex searching used by ldap
		"""
		# The Active Directory (AD) is organized into 2 ou's,
		# staff and freelance, so 2 calls need to be made
		users = []	# will be a list of user object to return
		server = ldap.initialize("ldap://a52dc01")
		# TODO: need a better anonymous login for browsing AD
		server.simple_bind_s("rush","area52")
		server.set_option(ldap.OPT_REFERRALS, 0)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_id)
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
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"sAMAccountName=%s" % user_id)
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
					obj.employment_status = 'freelance'
					users.append(obj)
		return users
	find_by_user_id = staticmethod(find_by_user_id)

	#@staticmethod
	def find_by_title(title=None):
		"""
		Search Active Directory and return
		a User object for each result
		"""
		# The Active Directory (AD) is organized into 2 ou's,
		# staff and freelance, so 2 calls need to be made
		users = []	# will be a list of user object to return
		server = ldap.initialize("ldap://a52dc01")
		# TODO: need a better anonymous login for browsing AD
		server.simple_bind_s("rush","area52")
		server.set_option(ldap.OPT_REFERRALS, 0)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"title=%s" % title)
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
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"title=%s" % title)
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
					obj.employment_status = 'freelance'
					users.append(obj)
		return users
	find_by_title=staticmethod(find_by_title)

	#@staticmethod
	def find_by_department(department=None):
		"""
		Search Active Directory and return
		a User object for each result
		Note: for now the search is limited to
		department until I can accomodate the 
		more complex searching used by ldap
		"""
		# The Active Directory (AD) is organized into 2 ou's,
		# staff and freelance, so 2 calls need to be made
		users = []	# will be a list of user object to return
		server = ldap.initialize("ldap://a52dc01")
		# TODO: need a better anonymous login for browsing AD
		server.simple_bind_s("rush","area52")
		server.set_option(ldap.OPT_REFERRALS, 0)
		result_id = server.search('ou=staff,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"Department=%s" % department)
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
		result_id = server.search('ou=freelance,ou=a52,dc=a52,dc=com',ldap.SCOPE_SUBTREE,"Department=%s" % department)
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
					obj.employment_status = 'freelance'
					users.append(obj)
		return users
	find_by_department = staticmethod(find_by_department)

	#@staticmethod
	def find_all():
		"""
		Get all users from both scopes ('staff' and 'freelance')
		"""
		users = []	# will be a list of user object to return
		server = ldap.initialize("ldap://a52dc01")
		# TODO: need a better anonymous login for browsing AD
		server.simple_bind_s("rush","area52")
		server.set_option(ldap.OPT_REFERRALS, 0)
		for scope in ['staff','freelance']:
			result_id = server.search('ou=%s,ou=a52,dc=a52,dc=com' % scope,ldap.SCOPE_SUBTREE,"cn=*")
			while 1:
				r_type, info = server.result(result_id, 0)
				if (info == []):
					break
				else:
					if r_type == 100:
						obj = User()
						user_id = info[0][1]['sAMAccountName'][0]
						#print "Adding %s user: %s" % (scope,user_id)
						obj.data = info[0][1]
						obj.user_id = user_id
						obj.cn = info[0][1]['cn'][0]
						obj.employment_status = scope
						users.append(obj)
		return users
	find_all = staticmethod(find_all)



if __name__ == '__main__':
	ids = []
	for user in User.find_all():
		ids.append(user.user_id)
	ids.sort()
	print ids

#	u = User()
#	u = User.find(user_id='robb')
#	print u.data
#	u.create_vTree(26)
#	users = User.find(department='discreet')
	#users = User.find(title='Producer')
#	print "U:",u
#	u[0].inspect()
#	users = u.find(department='discreet')
#	users = User.find(department='discreet')
#	for u in users:
#		u.inspect()
	pass



