
import re
import socket
import commands
import os
import time
import traceback
from datetime import datetime
from datetime import timedelta
#from paramiko import *
from settings import *
from A52.utils import print_array
from A52.utils import messenger 
from A52.License import Server,Daemon,Feature,User

import logging
log = logging.getLogger(__name__)

#tmy@ripley:/Volumes/discreet/dev/python2.3/site-packages/A52/License/flexlm$ ssh root@192.168.78.59
#root@192.168.78.59's password: 
#Last login: Mon Jul 11 09:45:25 2011 from 192.168.98.71
#[root@nysmoke01 ~]# /usr/discreet/licserv/lmutil lmstat -c /usr/discreet/licserv/licenses/DL_license.dat -a


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


class FlexlmException(Exception):
	pass

class flexlm(ssh):
	"""
	Handler class for flexlm utilties

	Info:
	/usr/discreet/licserv/lmutil lmstat -A -c /usr/local/flexlm/licenses/aw_burnman.dat

	Remove:
	/usr/discreet/licserv/lmutil lmremove -c /usr/local/flexlm/licenses/aw_burnman.dat -h 85537MAYAMMR2_F burnman 27005 23740
	# non license file version
	/usr/local/bin/lmutil lmremove -c 7112@don -h burn_x86_64_r_2012 don 7112 998

	Don:
	/usr/local/ISL/FLEXlm/lmutil lmstat -a  /var/flexlm/adsk_server.lic
	
	"""

	def __init__(self,hostname,port=None):
		self.hostname=hostname
		self.port=port
		self.lmstat()

	def __iter__(self):
		"""
		Iterate over the servers,
		the server's daemons,
		and the daemon's features
		stored in this object
		"""
		for server in self.servers:
			for daemon in server.daemons:
				for feature in daemon.features:
					yield (server,daemon,feature)

	def status(self):
		"""
		Simple up / down status
		of the license server.
		"""
		if self.servers[0].status == 'UP':
			return True
		return False

	def lmstat(self):
		#f = open('/Volumes/discreet/dev/python2.3/site-packages/A52/License/flexlm/lmstat_output.txt')
		#output = f.readlines()
		#f.close()
		self.lmstat_output = lmutil.lmstat(self.hostname,self.port)
		# get a list of server objects from
		# the lmstat parser
		p = parser()
		self.servers = p.parse_lmstat(self.lmstat_output)
		self.server = p.parse_lmstat(self.lmstat_output)[0]
		# add the expiration dates which 
		# is a separate call
		self._get_expiry()

	def restart(self):
		"""
		Restart the flexlm server
		"""
		out,err = self.ssh(self.hostname,'date')
		log.info(out)

	def _get_expiry(self):
		"""
		Check the expiration dates
		on the features on the server
		"""
		output = lmutil.lmdiag(self.hostname,self.port)
		# get a list of server objects from
		# the lmstat parser
		p = parser()
		self.expiry = p.parse_lmdiag(output)
		for server,daemon,feature in self:
			key = "%s@%s" % (server.port,server.host)
			try:
				exp_info = self.expiry[key][daemon.name][feature.name]
			except:
				#traceback.print_exc()
				# no expiry info
				pass
			else:
				feature.__dict__.update(exp_info)
				if exp_info['expires']:
					feature.exp_datetime = datetime(*time.strptime(exp_info['expires'],"%d-%b-%Y")[0:6])
				else:
					feature.exp_datetime = None
				if exp_info['starts']:
					feature.start_datetime = datetime(*time.strptime(exp_info['starts'],"%d-%b-%Y")[0:6])
				else:
					feature.start_datetime = None

	def check_expiry(self,days=10):
		"""
		Check features for expiration dates
		that occur within 'x' days and 
		send a warning email
		"""
		now = datetime.today()
		for server,daemon,feature in self:
			print "Feature: %s  Expires: %s" % (feature.name,feature.exp_datetime)
			if feature.exp_datetime and feature.exp_datetime > now-timedelta(days=days):
				if server.license_files:
					license_file = server.license_files[0].strip()
				else:
					license_file = 'unknown'
				self._expiration_notify(	server.host,
									server.port,
									daemon.name,
									feature.name,
									license_file,
									feature.exp_datetime-now)
				break

	def _expiration_notify(self,host,port,daemon,feature,license_file,delta):
		"""
		Email a warning about a license expiration
		"""
		from_addr = 'eng@a52.com'
		#to_addrs = 'eng@a52.com'
		to_addrs = 'tommy.hooper@a52.com'
		subject = "License Expiration Warning"
		msg = "The following license will expire soon:\n"
		msg+= "Feature: %s\n" % feature
		msg+= "License server: %s\n" % host
		msg+= "Port: %s\n" % port
		msg+= "License file: %s\n" % license_file
		msg+= "Daemon: %s\n" % daemon
		msg+= "Time remaining: %s\n" % delta
		print msg
		#messenger.Email(from_addr,to_addrs,subject,msg)


	def list_all(self,daemons=True,features=True,users=True,verbose=True):
		self._list_servers(daemons=daemons,features=features,users=users,verbose=verbose)

	def _list_servers(self,**kwargs):
		for s in self.servers:
			if kwargs['verbose']:
				print "Server: %s on port %s" % (s.host,s.port)
			else:
				print "%s@%s" % (s.host,s.port)
			if kwargs['daemons']: self._list_daemons(s,**kwargs)

	def _list_daemons(self,server,**kwargs):
		for d in server.daemons:
			if kwargs['verbose']:
				print "\tDaemon: %s" % d.name
				print "\tStatus: %s" % d.status
				print "\tVersion: %s" % d.version
			else:
				print d.name
			if kwargs['features']: self._list_features(d,**kwargs)

	def _list_features(self,daemon,**kwargs):
		for f in daemon.features:
			if kwargs['verbose']:
				print "\t\tFeature: %s" % f.name
				print "\t\t\tLicense Type: %s" % f.type
				print "\t\t\tVersion: %s" % f.version
				print "\t\t\tVendor: %s" % f.vendor
				print "\t\t\tTotal licenses: %s" % f.total
				print "\t\t\tTotal in use: %s" % f.in_use
			else:
				print f.name
			if kwargs['users']: self._list_users(f,**kwargs)

	def _list_users(self,feature,**kwargs):
		for u in feature.users:
			if kwargs['verbose']:
				print "\t\t\t\tUser: %s" % u.user
				print "\t\t\t\t\tHost: %s" % u.host1
				print "\t\t\t\t\tHost_2: %s" % u.host2
				print "\t\t\t\t\tID: %s" % u.id_num
				print "\t\t\t\t\tVersion: %s" % u.version
				print "\t\t\t\t\tStart: %s" % " ".join(u.start_time)
			else:
				print u.user

	#@staticmethod
	def list_ports(host):
		"""
		List the known ports for
		the given 'host'
		"""
		if COMMANDS.has_key(host):
			return COMMANDS[host].keys()
		else:
			print "Error: Unknown host %s" % host
			return []
	list_ports = staticmethod(list_ports)

class lmutil:


	def __init__(self):
		pass

	def lmremove(server,feature,host,port,handle):
		# "/usr/discreet/licserv/lmutil lmremove -c /usr/local/flexlm/licenses/aw_burnman.dat -h 85537MAYAMMR2_F burnman 27005 23740"
		command = "/usr/local/bin/lmutil lmremove -c %s@%s -h %s %s %s %s" % (port,server,feature,server,port,handle)
		log.info("Executing: %s" % command)
		log.info(commands.getoutput(command))
	lmremove = staticmethod(lmremove)

	#@staticmethod
	def lmstat(hostname,port,opt_all=True):
		#command = "/usr/local/ISL/FLEXlm/lmutil lmstat -a  /var/flexlm/adsk_server.lic"
		#command = "/usr/local/bin/lmutil lmstat -a -c %s" % license_file
		if opt_all:
			opt_all = "-a"
		else: 
			opt_all = ""
		command = "/usr/local/bin/lmutil lmstat -c %s@%s %s" % (port,hostname,opt_all)
		log.info(command)
		return commands.getoutput(command)
	lmstat = staticmethod(lmstat)

	def lmdiag(hostname,port):
		#command = "/usr/local/bin/lmutil lmdiag -n -c 7112@don" 
		command = "/usr/local/bin/lmutil lmdiag -c %s@%s -n" % (port,hostname)
		log.info(command)
		return commands.getoutput(command)
	lmdiag = staticmethod(lmdiag)

class _lmstat_parser:


	def __init__(self):
		pass

	def parse(self,output):
		"""
		Parse the output of the lmstat command
		and create a dictionary representation of the 
		information.
		"""
		servers = []
		context = None
		for line in output.split('\n'):
			#line = line.strip()
			# first check for context lines. One of:
			if line.find("License server status:") >= 0:
				# License server status: 27000@don			# server context
				context = 'server'
				port,host = line.split(':')[1].strip().split('@')
				current_server = Server(host,port)
				servers.append(current_server)
			elif line.find("Vendor daemon status ") >= 0:
				# Users of burn_x86_64_r_2011_1:  (Error: 1000000 licenses, unsupported by licensed server)
				# Vendor daemon status (on don.a52.com):		# daemon context
				context = 'daemon'
				current_daemon = Daemon(current_server)
				current_server.add_daemon(current_daemon)
			elif line.find("Users of") >= 0:
				# Feature usage info:					# feature context
				context = 'feature'
				current_feature = Feature(current_daemon)
				current_daemon.add_feature(current_feature)
			elif "start" in line and line.split() > 8:
				# andyl cg07 cg07 (v1.000) (don/27000 14501), start Fri 7/8 2:36	# user line
				context = 'user'
				current_user = User(current_feature)
				current_feature.add_user(current_user)
			elif "Error" in line:
				# Error getting status: Cannot connect to license server system. (-15,570:115 "Operation now in progress")
				raise FlexlmException,line

			if context == 'server':
				current_server.__dict__.update(self._parse_server_line(line))
			elif context == 'daemon':
				current_daemon.__dict__.update(self._parse_daemon_line(line))
			elif context == 'feature':
				current_feature.__dict__.update(self._parse_feature_line(line))
			elif context == 'user':
				current_user.__dict__.update(self._parse_user_line(line))
		return servers

	def _parse_server_line(self,line):
		"""
		    License file(s) on don: /var/flexlm/adsk_server.lic:
		           don: license server UP (MASTER) v11.7
		"""
		if "License file(s)" in line:
			#License file(s) on don: /var/flexlm/adsk_server.lic:
			license_files = line.split(':')[1:]
			return {'license_files':license_files[0:len(license_files)-1]}
		elif "license server" in line:
			# don: license server UP (MASTER) v11.7
			# don: license server UP v10.8
			if len(line.split()) == 6:
				status,srv_type,version = line.split()[3:6]
			elif len(line.split()) == 5:
				status,version = line.split()[3:5]
				srv_type = 'unknown'
			return {'status':status,'type':srv_type.lstrip('(').rstrip(')'),'version':version}
		return {}

	def _parse_daemon_line(self,line):
		if "Vendor daemon status" not in line\
			and "Feature usage info:" not in line\
			and len(line):
			# foundry: UP v10.8
#			print "\t\tPARSE:",line
			name,status,version = line.split()
			return {'name':name.rstrip(':'),'status':status,'version':version}
		return {}

	def _parse_feature_line(self,line):
		if 'Users of' in line:
			# Users of 85530MAYAMMR_F:  (Total of 18 licenses issued;  Total of 5 licenses in use)
			# Users of wiretapgw_all_r_2011_1:  (Error: 6 licenses, unsupported by licensed server)
			# Users of burn_x86_64_r_2011_1:  (Error: 1000000 licenses, unsupported by licensed server)
			# Users of tinder_discreet_i:  (Uncounted, node-locked)
			name = line.split()[2].rstrip(':')
			if "Error" in line:
				total = line.split()[4]
				in_use = line.split()[6]
			elif line.split()[4].strip(')') == 'node-locked':
				total = 1
				in_use = 'uncounted'
			else:
				total = line.split()[5]
				in_use = line.split()[10]
			if FEATURES.has_key(name):
				group = FEATURES[name]
				group_label = FEATURES[name]
			else:
				group = name
				group_label = name
			return {'name':name,'total':total,'in_use':in_use,'group':group,'group_label':group_label}
		elif 'vendor' in line:
			# "85530MAYAMMR_F" v1.000, vendor: adskflex
			version = line.split()[1].rstrip(',')
			vendor = line.split()[3]
			return {'version':version,'vendor':vendor}
		elif 'license' in line:
			# floating license
			return {'type':line.strip()}
		return {}

	def _parse_user_line(self,line):
		# andyl cg07 cg07 (v1.000) (don/27000 14501), start Fri 7/8 2:36
		if len(line.split()) == 10:
			user = line.split()[0]
			host1 = line.split()[1]
			host2 = line.split()[2]
			version = line.split()[3].lstrip('(').rstrip(')')
			id_num = line.split()[5].rstrip('),')
			start_time = line.split()[7:]
		elif len(line.split()) == 9:
			user = line.split()[0]
			host1 = line.split()[1]
			host2 = None
			version = line.split()[2].lstrip('(').rstrip(')')
			id_num = line.split()[4].rstrip('),')
			start_time = line.split()[6:]
		else:
			return {}
		return {	'user':user,	
				'host1':host1,
				'host2':host2,
				'version':version,
				'id_num':id_num,
				'start_time':start_time}

	def _parse_error_line(self,line,context):
		# Error getting status: Cannot connect to license server system. (-15,570:115 "Operation now in progress")
		if len(line.split()) == 10:
			user = line.split()[0]
			host1 = line.split()[1]
			host2 = line.split()[2]
			version = line.split()[3].lstrip('(').rstrip(')')
			id_num = line.split()[5].rstrip('),')
			start_time = line.split()[7:]
		elif len(line.split()) == 9:
			user = line.split()[0]
			host1 = line.split()[1]
			host2 = None
			version = line.split()[2].lstrip('(').rstrip(')')
			id_num = line.split()[4].rstrip('),')
			start_time = line.split()[6:]
		else:
			return {}
		return {	'user':user,	
				'host1':host1,
				'host2':host2,
				'version':version,
				'id_num':id_num,
				'start_time':start_time}


class _lmdiag_parser:


	def __init__(self):
		self.re_feature_line = re.compile('"(.*)" *(v[0-9\.]*), *vendor: (.*)')
		self.re_expiry_line = re.compile('^(.*)starts: *([0-9]+-[A-z]{3}-[0-9]{4}), *(.*)')
		self.re_divider_line = re.compile('^-*$')

	def parse(self,output):
		"""
		Parse the output of the lmdiag command
		and create a dictionary representation of the 
		information.
		"""
		expiry =  {}
		context = None
		for line in output.split('\n'):
			line = line.strip()
			if line.find("License file:") >= 0:
				# License file: 7112@don
				port,host = line.split(':')[1].strip().split('@')
				server = "%s@%s" % (port,host)
				context = 'server'
				if not expiry.has_key(server):
					expiry[server] = {}
			elif line.find("vendor") >= 0:
				# "burn_x86_64_r_2012_1" v2012.999, vendor: discreet_l
				feature,version,vendor = self._parse_feature_line(line)
				daemon = vendor
				context = 'daemon'
				if not expiry[server].has_key(daemon):
					expiry[server][daemon] = {}
				if not expiry[server][daemon].has_key(feature):
					expiry[server][daemon][feature] = {}
				expiry[server][daemon][feature]['version'] = version
			elif "starts" in line and line.split() > 5:
				# floating license  starts: 1-jan-1990,  no expiration date
				info = self._parse_expiry_line(line)
				expiry[server][daemon][feature].update(info)
				context = 'expiry'
			elif line.find("This license can be checked out") >= 0:
				expiry[server][daemon][feature]['valid'] = True
				context = 'validity'
				expiry[server][daemon][feature]['valid_msg'] = [line]
			elif line.find("This license cannot be checked out because") >= 0:
				expiry[server][daemon][feature]['valid'] = False
				expiry[server][daemon][feature]['valid_msg'] = [line]
				context = 'validity'
				validity_message = []
			elif context == 'validity' and line != "" and not re.match(self.re_divider_line,line):
				expiry[server][daemon][feature]['valid_msg'].append(line)
			elif "Error" in line:
				raise FlexlmException,line
		return expiry

	def _parse_feature_line(self,line):
		match = re.match(self.re_feature_line,line)
		if match:
			feature,version,vendor = match.groups()
		else:
			feature,version,vendor = [None,None,None]
		return feature,version,vendor
		
	def _parse_expiry_line(self,line):
		# floating license  starts: 1-jan-1990,  no expiration date
		match = re.match(self.re_expiry_line,line)
		if match:
			lc_type,start_date,exp_tag = match.groups()
			if 'expires' in exp_tag:
				exp_date = exp_tag.split(':')[1].strip()
			else:
				exp_date = None
			return {	'type':lc_type,
					'starts':start_date,
					'expires':exp_date}
		return {}
		


class parser:


	def __init__(self):
		pass
	
	def parse_lmstat(self,output):
		prsr = _lmstat_parser()
		return prsr.parse(output)

	def parse_lmdiag(self,output):
		prsr = _lmdiag_parser()
		return prsr.parse(output)

if __name__ == '__main__':
#	print flexlm.list_ports('don')
	pass
	#f = flexlm('don',27000)
	#f.check_expiry()


#	for port in flexlm.list_ports('tom'):
#		try:
#			f = flexlm('tom',port)
#			f.list_all(users=True,verbose=True)
#		except:pass
#	f = flexlm('tom',7113)
	f = flexlm('don',27003)
	f.list_all()
#	for ft in f.servers[0].daemons[0].features:
#		print dir(ft)
#	f.list_all(users=True,verbose=True)
#	print lmutil.lmstat('tom',7113)


#	for port in FLEXLM_COMMANDS['tom']:
#		try:
#			flm = flexlm('tom',port)
#			#f.list_all()
#		except: pass
#		else:
#			for s,d,f in flm:
#				print s,d,f
			

#	f = flexlm('nysmoke',27000)
#	print f.status()
#	if not f.status():
#	f.restart()
#	print lmutil.lmstat('don',7112)
#	print "Servers:",f.servers
#	f.list_all(users=True,verbose=True)
#	f.servers[0].list_daemons()
#	f.servers[0].daemons[0].list_features()
#	f.servers[0].daemons[0].features[0].list_users()
#	users = f.servers[0].daemons[0].features[0].users
#	user = users[len(users)-1]
#	user.info()
#	user.remove()








