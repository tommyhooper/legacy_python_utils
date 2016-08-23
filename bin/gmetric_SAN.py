#!/usr/bin/python

import os,re,sys,socket
sys.path.append('/disks/nas2/discreet/lib/python2.3/site-packages')
import A52
from A52.utils import print_array

class ifstat:
	def __init__(self):
		"""
		Main loop for the daemon
		"""
		self.statefile ="/var/lib/ganglia/metrics/SAN.stats"
		self.sanfile_dir ="/var/lib/ganglia/SAN_files"
		#self.hostname = socket.gethostname()
		self.hostname = 'flame1'
		self.gmetric = '/usr/bin/gmetric'
		self.find_sans()

		# get values from the statefile
		self.get_state()
		self.get_stats()
		self.get_delta()
		self.exec_gmetric()
		self.store_state()


	def get_state(self):
		self.state={}
		if os.access(self.statefile,os.R_OK):
			f = open(self.statefile,'ro')
			for line in f.readlines():
				blkdev,stat,value = line.strip().split(':')
				try: 		self.state[blkdev][stat] = value
				except:	self.state[blkdev] = {stat:value}
			f.close()

	def store_state(self):
		if not os.access(os.path.dirname(self.statefile),os.R_OK):
			os.makedirs(os.path.dirname(self.statefile))
		# store the current state
		f = open(self.statefile,'w')
		for blkdev in self.blkdevs:
			for stat in self.blkdevs[blkdev]:
				line = "%s:%s:%s" % (blkdev,stat,self.blkdevs[blkdev][stat])
				f.write(line+"\n")
		f.close()

	def get_delta(self):
		self.delta = {}
		for blkdev in self.blkdevs:
			if not self.delta.has_key(blkdev):self.delta[blkdev] = {}
			for stat in self.blkdevs[blkdev]:
				if self.state.has_key(blkdev):
					state_value = self.state[blkdev][stat]
				else:
					state_value = 0
				stat_value = self.blkdevs[blkdev][stat]
				delta = int(stat_value) - int(state_value)
				if delta < 0:
					delta = 0
				self.delta[blkdev][stat] = delta

	def find_sans(self):
		"""
		Unknown SAN:
		"F5412SATA03L0"
		"F5412SATA03L1"
		"""
		self.sans = {	'SANSTONE01':["F6412SAS01L0","F6412SAS01L1"],
					'SANSTONE02':["F6412SAS02L0","F6412SAS02L1"],
					'SANSTONE03':["F6412SAS03L0","F6412SAS03L1"],
					'SANSTONE04':["F6412SATA02L0","F6412SATA02L1"],
					'SANSTONE05':["F5412SATA01L0","F5412SATA01L1"],
					'SANSTONE06':["F5412SATA02L0","F5412SATA02L1"],
					'SANSTONE07':["F6412SATA01L0","F6412SATA01L1"]}
		self.luns = {}
		self.blkdevs = {}

		# open the host .san file and find each san's block devices
		fl = open('%s/%s.san' % (self.sanfile_dir,self.hostname))
		lines = fl.readlines()
		for line in lines:
			regx = re.match('.*(/dev/[a-z]*).*(".*")',line)
			if regx:
				blkdev = os.path.basename(regx.group(1))
				lun = regx.group(2).strip('"')
				self.luns[lun] = blkdev
				self.blkdevs[blkdev] = None

	def get_stats(self):
		# get the stats for the interfaces:
		f = open('/proc/diskstats','r')
		index = 2
		lines = f.readlines()
		dstat = {}
		while (index < len(lines)):
			line = lines[index].split()
			if len(line) == 14:
				# only grab the lines that actually change
				dstat[line[2]] = {
					'read_issued':line[3],
					'reads_merged':line[4],
					'sectors_read':line[5],
					'millisec_reading':line[6],
					'writes_completed':line[7],
					'writes_merged':line[8],
					'sectors_written':line[9],
					'millisec_writing':line[10],
					'ios_in_prog':line[11],
					'millisec_ios':line[12],
					'millisec_ios_weighted':line[13]}
			index+=1
		for blkdev in self.blkdevs:
			self.blkdevs[blkdev] = dstat[blkdev]

	def exec_gmetric(self):
		# form and execute the gmetric commands
		for stone,luns in self.sans.items():
			for lun in luns:
				blkdev = self.luns[lun]
				label = "%s_%s" % (stone,lun[-2:])
				read_command = self.gmetric+" --name %s_read --value %s --type int32" % (label,self.delta[blkdev]['sectors_read'])
				write_command = self.gmetric+" --name %s_write --value %s --type int32" % (label,self.delta[blkdev]['sectors_written'])
				os.system(read_command)
				os.system(write_command)
				#print "Read:",read_command
				#print "Write:",write_command


if __name__ == "__main__":
	i = ifstat()


#flame1 : F6412SAS01
#flame2 : F6412SAS02
#flame3 : F6412SAS03
#flame4 : F6412SATA02
#flare1 : F5412SATA02
#smoke2 : F6412SATA01
#smack1 : F5412SATA01

# cat /proc/diskstats | grep sda
#8 0 sda 2461810 61427 148062742 6482992 660009 1544934 67900384 45642376 0 7162961 52128751
#[3]: # of reads issued
#[4]: # of reads merged
#[5]: # of sectors read
#[6]: # of milliseconds spent reading
#[7]: # of writes completed
#[8]: # of writes merged
#[9]: # of sectors written
#[10]: # of milliseconds spent writing
#[11]: # of I/Os currently in progress
#[12]: # of milliseconds spent doing I/Os
#[13]: weighted # of milliseconds spent doing I/Os

#/dev/sdl   [XYRATEX F5412E              ] SNFS "F5412SATA01L0"  Sectors: 7735044063. SectorSize: 512.  Maximum sectors: 7735044063.
#/dev/sdaa  [XYRATEX F5412E              ] SNFS "F5412SATA01L1"  Sectors: 7735044063. SectorSize: 512.  Maximum sectors: 7735044063.
