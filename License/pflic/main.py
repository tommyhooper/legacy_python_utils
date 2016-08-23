
import re
import socket
import commands
import os
import time
import traceback
import socket
from datetime import datetime
from datetime import timedelta
from A52.utils import print_array
from A52.License import Server,Daemon,Feature,User

import urllib
import urllib2

import xml.etree.cElementTree as ElementTree



class pflic:

	HOST = 'don'
	PORT = 8071
	URL = "http://%s:%s/status.xml" % (HOST,PORT)

	def __init__(self):
		self.get_status()

	def get_status(self):
		"""
		TAG: version
		TAG: hostid
		TAG: availableLicenses
		TAG: usedLicenses
		"""
		xml = self._get_xml()
		self.tree = ElementTree.XML(xml)

		self.server = Server(self.HOST,self.PORT)
		self.server.version = self.tree.find('version').text
		self.server.hostid = self.tree.find('hostid').text

		daemon = Daemon(self.server)
		daemon.name = 'pflic'

		self._get_features(daemon)

	def _get_features(self,daemon):
		avail = self._get_available_licenses(self.tree)
		used = self._get_used_licenses(self.tree)

		features = {}
		users = {}
		for i,a in avail.iteritems():
			print a



#		print "VERSION:",self.version
#		print "HOSTID:",self.hostid
#		print "AVAILABLE:"
#		print_array(self.available_licenses)
#		print "USED:"
#		print_array(self.used_licenses)

	def _get_xml(self):
		page = urllib2.urlopen(self.URL);
		xml = page.read()
		return xml

	def _get_available_licenses(self,tree):
		avail = {}
		i = 0
		for node in tree.findall('availableLicenses'):
			for license in node:
				avail[i] = {}
				for attr in license:
					avail[i][attr.tag] = attr.text
					if attr.tag == 'ip':
						avail[i]['host'] = self._resolve_ip(attr.text)
				i+=1
		return avail

	def _get_used_licenses(self,tree):
		used = {}
		i = 0
		for node in tree.findall('usedLicenses'):
			for license in node:
				used[i] = {}
				for attr in license:
					used[i][attr.tag] = attr.text
					if attr.tag == 'ip':
						used[i]['host'] = self._resolve_ip(attr.text)
				i+=1
		return used

	def _resolve_ip(self,ip):
		try:
			return socket.gethostbyaddr(ip)[0]
		except:
			return None



if __name__ == '__main__':
	p = pflic()
#	p.get_status()
	pass


"""
VERSION: 3.0.0
HOSTID: e5d3f97b6f8f
AVAILABLE:
 * 0 =>
	 + count => 2
	 + expiryDate => permanent
	 + feature => PFTrack
	 + version => 2012
 * 1 =>
	 + count => 2
	 + expiryDate => permanent
	 + feature => PFTrack
	 + version => 2011.0
 * 2 =>
	 + count => 2
	 + expiryDate => permanent
	 + feature => PFTrack
	 + version => 5.0
USED:
 * 0 =>
	 + checkoutTime => 2013-03-01 18:34:01
	 + feature => PFTrack
	 + host => cg22.a52.com
	 + ip => 192.168.97.86
	 + version => 2012
 * 1 =>
	 + checkoutTime => 2013-03-20 10:44:40
	 + feature => PFTrack
	 + host => cg25.a52.com
	 + ip => 192.168.97.89
	 + version => 2012

"""





