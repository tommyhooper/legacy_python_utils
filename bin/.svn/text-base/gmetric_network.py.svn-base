#!/usr/bin/python

#import sys,string
import os,re,sys
sys.path.append('/disks/nas2/discreet/lib/python2.3/site-packages')
from A52.utils.daemon import Daemon

class ifstat(Daemon):

	def __init__(self):
		"""
		Main loop for the daemon
		"""
		Daemon.__init__(self,None)
		self.if_cmd = 'netstat -r'
		self.gmetric = '/usr/bin/gmetric'
		self.ifkey = 	{
					'88':'Infiniband',
					'96':'Burn',
					'97':'Gige-1',
					'98':'Gige-2',
					'99':'SAN_meta',
					'101':'mgt'
					}
		self.interfaces = self.find_interfaces()

		# get values from the statefile
		self.statefile ="/var/lib/ganglia/metrics/net.stats"
		self.get_state()
		self.get_stats()
		self.exec_gmetric()
		self.store_state()

	def get_state(self):
		if os.access(self.statefile,os.R_OK):
			f = open(self.statefile,'ro')
			for line in f.readlines():
				if_name,stat,value = line.strip().split(':')
				self.interfaces[if_name][stat] = value
			f.close()

	def store_state(self):
		if not os.access(os.path.dirname(self.statefile),os.R_OK):
			os.makedirs(os.path.dirname(self.statefile))
		# store the current state
		if self.interfaces:
			f = open(self.statefile,'w')
			for if_name in self.interfaces:
				for stat in self.interfaces[if_name]:
					f.write("%s:%s:%s\n" % (if_name,stat,self.interfaces[if_name][stat]))
			f.close()

	def run(self):
		while True:
			if self.interfaces:
				if self.get_stats():
					self.exec_gmetric()

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
										'TX_delta':0,
										'RX_bytes':0,
										'RX_delta':0
										}
		
			index+=1
		return interfaces

	def get_stats(self):
		# get the stats for the interfaces:
		f = open('/proc/net/dev','r')
		index = 2
		lines = f.readlines()
		while (index < len(lines)):
			line = lines[index]
			if_name,stats = line.strip().split(":")
			stats = re.sub(" +",' ',stats.strip("\n").strip()).split(' ')
			#  0       1      2   3    4     5        6         7       8      9     10   11   12   13     14       15
			# bytes packets errs drop fifo frame compressed multicast|bytes packets errs drop fifo colls carrier compressed
			#       0            1        2    3    4    5    6       7            8           9      10   11   12   13   14   15  
			# ['5900481471', '18862356', '0', '0', '0', '0', '0', '8153007', '1592173813', '4654625', '0', '0', '0', '0', '0', '0']
			rx_bytes = stats[0]
			packets_in = stats[1]
			multicast = stats[7]
			tx_bytes = stats[8]
			patckets_out = stats[9]
			if self.interfaces.has_key(if_name):
				# figure out the delta since last poll
				if self.interfaces[if_name]['TX_bytes']:
					self.interfaces[if_name]['TX_delta'] = int(tx_bytes) - int(self.interfaces[if_name]['TX_bytes'])
				if self.interfaces[if_name]['RX_bytes']:
					self.interfaces[if_name]['RX_delta'] = int(rx_bytes) - int(self.interfaces[if_name]['RX_bytes'])
				# if the stat is negative there was probably a reboot so the packet count started over
				if tx_bytes < 0:
					tx_bytes = 0
				if rx_bytes < 0:
					rx_bytes = 0
				self.interfaces[if_name]['TX_bytes'] = tx_bytes
				self.interfaces[if_name]['RX_bytes'] = rx_bytes
			index+=1
		return True


	def exec_gmetric(self):
		# form and execute the gmetric commands
		for key in self.interfaces:
			tx_command = self.gmetric+" --name %(name)s_TX --value %(TX_delta)s --type int32" % (self.interfaces[key])
			rx_command = self.gmetric+" --name %(name)s_RX --value %(RX_delta)s --type int32" % (self.interfaces[key])
			os.system(tx_command)
			os.system(rx_command)
			#print "TX:",tx_command
			#print "RX:",rx_command

if __name__ == "__main__":
	try:
		# start/stop/restart the daemon
		if sys.argv[1] == "-d":
			daemon = ifstat('/tmp/gmetric_network.pid')
			if len(sys.argv) == 2:
				if 'start' == sys.argv[1]:
					daemon.start()
				elif 'stop' == sys.argv[1]:
					daemon.stop()
				elif 'restart' == sys.argv[1]:
					daemon.restart()
				else:
					print "Unknown command"
					sys.exit(2)
				sys.exit(0)
		else:
			print "usage: %s start|stop|restart" % sys.argv[0]
			sys.exit(2)
	except:
		# or just run it once
		i = ifstat()

