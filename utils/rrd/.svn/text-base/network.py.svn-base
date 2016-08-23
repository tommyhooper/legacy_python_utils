#!/usr/bin/python

import os,re,sys,socket
from A52 import utils
from A52.utils import print_array
from main import rrd
import fcntl
import struct
import array

class netstat(rrd):
	def __init__(self):
		"""
		Main loop for the daemon
		"""
		self.hostname = socket.gethostname()
		self.fqdn = socket.getfqdn()
		if self.fqdn == 'localhost':
			self.fqdn = self.hostname
		self.rrd_dir = '/Volumes/discreet/lib/ganglia/rrds/%s' % self.fqdn
		self.ifkey = 	{
					'88':'Infiniband',
					'96':'Burn',
					'97':'Gige-1',
					'98':'Gige-2',
					'99':'SAN_meta',
					'101':'mgt'
					}
		return


	def run(self):
		"""
		Run one cycle of this class
		"""
		self.update_rrds()

	def update_rrds(self):
		"""
		Insert the current stats into the net rrds
		"""
		# find the active interfaces
		interfaces = self.active_interfaces()
		# get the stats from the san's block devices
		stats = self.get_stats()
		# form and execute the rrd commands
		for name,ip in interfaces.iteritems():
			if name == 'lo':pass
			elif stats.has_key(name):
				rrd_file = "%s/net_%s.rrd" % (self.rrd_dir,ip)
				if not os.path.exists(rrd_file):
					self.create_rrds()
				bytes_read = stats[name]['RX_bytes']
				bytes_written = stats[name]['TX_bytes']
				values = "%s:%s" % (bytes_read,bytes_written)
				#print "self.update_rrd(",rrd_file,'N',values
				self.update_rrd(rrd_file,'N',values)

	def active_interfaces(self):
		max_possible = 128  # arbitrary. raise if needed.
		bytes = max_possible * 32
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		names = array.array('B', '\0' * bytes)
		outbytes = struct.unpack('iL', fcntl.ioctl(
			s.fileno(),
			0x8912,  # SIOCGIFCONF
			struct.pack('iL', bytes, names.buffer_info()[0])
			))[0]
		namestr = names.tostring()
		interfaces = {}
		for i in range(0, outbytes, 40):
			name = namestr[i:i+16].split('\0', 1)[0]
			ip   = socket.inet_ntoa(namestr[i+20:i+24])
			interfaces[name] = ip
		return interfaces

	def create_rrds(self):
		"""
		Create the concurrent user rrd file
		"""
		# check for the host directory:
		if not os.path.exists(self.rrd_dir):
			utils.makedirs(self.rrd_dir)

		interfaces = self.active_interfaces()
		for name,ip in interfaces.iteritems():
			rrd_file = "%s/net_%s.rrd" % (self.rrd_dir,ip)
			if name == 'lo': pass
			elif not os.path.exists(rrd_file):
				rrdcreate = "rrdtool create"
				args = " %s" % (rrd_file)
				args+= " DS:bytes_read:COUNTER:60:0:30000000000000"
				args+= " DS:bytes_written:COUNTER:60:0:30000000000000"
				args+= " RRA:AVERAGE:0.5:12:2000" 
				command = rrdcreate+args
				print "COMMAND:",command
				os.system(command)
		
	def get_stats(self):
		# get the stats for the interfaces:
		f = open('/proc/net/dev','r')
		index = 2
		lines = f.readlines()
		interfaces = {}
		while (index < len(lines)):
			line = lines[index]
			if_name,stats = line.strip().split(":")
			stats = re.sub(" +",' ',stats.strip("\n").strip()).split(' ')
			#  0       1      2   3    4     5        6         7       8      9     10   11   12   13     14       15
			# bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
			#       0            1        2    3    4    5    6       7            8           9      10   11   12   13   14   15  
			# ['5900481471', '18862356', '0', '0', '0', '0', '0', '8153007', '1592173813', '4654625', '0', '0', '0', '0', '0', '0']
			rx_bytes = stats[0]
			tx_bytes = stats[8]
			interfaces[if_name] = {'TX_bytes':tx_bytes,'RX_bytes':rx_bytes}
			index+=1
		return interfaces

	def find_interfaces(self):
		# get the interfaces:
		interfaces = {}
		stdin, stdout = os.popen2(self.if_cmd,'t')
		index = 2
		lines = stdout.readlines()
		while (index < len(lines)):
			line = re.sub(" +",' ',lines[index].strip("\n")).split(' ')
			try:
				neta,netb,netc,netd = line[0].split('.')
				if_name = line[7]
			except:pass
			else:
				if neta == '192':
					if self.ifkey.has_key(netc):
						interfaces[if_name] = 	{
										'name':self.ifkey[netc],
										'TX_bytes':0,
										'RX_bytes':0,
										}
		
			index+=1
		return interfaces

if __name__ == "__main__":
	pass
