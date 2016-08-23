#!/usr/bin/env python

from models import mailing_lists
from models import mailing_list_map
from models import email_addresses
from A52.db import controller
from A52.utils import print_array
db = controller()

import datetime
import time
#import logging
import sys
import os


class MailingList(mailing_lists):


	def __init__(self,**kwargs):
		"""
		Mailing List Object
		"""
		self.domain = 'a52.com'
		self.data = {}
		self.data.update(kwargs)

	def get_emails(self,source='db'):
		"""
		Get mailing lists assigned to 
		the mailing list
		"""
		if source == 'db':
			return self._get_db_emails()
		else:
			pass
			# TODO: incorporate gam portal 
			#return self._get_gam_emails()

	def _get_db_emails(self):
		"""
		Get emails for this mailing list
		from the db
		"""
		emails = []
		sel = """	select
					ea.uid,
					ea.address,
					ea.user_id,
					ea.domain,
					ea.first_name,
					ea.last_name
				from
					mailing_list_map
					as mlm
				left join
					email_addresses as ea
					on mlm.email_address_uid=ea.uid
				where
					mailing_list_uid = '%s'
			""" % (self.data['uid'])
		rows = db.select(database='a52_production',statement=sel)
		for row in rows:
			obj = EmailAddress(	uid=row['uid'],
							address=row['address'],
							user_id=row['user_id'],
							domain=row['domain'],
							first_name=row['first_name'],
							last_name=row['last_name'])
			emails.append(obj)
		return emails


class EmailAddress(email_addresses):
	

	def __init__(self,**kwargs):
		"""
		Email Address Object
		"""
		self.data = {}
		self.data.update(kwargs)


class MailingListMap(mailing_list_map):


	def __init__(self,**kwargs):
		"""
		Mailing List Map Object
		"""
		self.data = {}
		self.data.update(kwargs)




if __name__ == '__main__':
	m = MailingList.find(uid=4)[0]
	m.get_emails()
	pass








