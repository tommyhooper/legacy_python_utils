#!/usr/bin/python

import os,re,sys,socket
from A52 import utils
from A52.utils import print_array
from main import rrd

class SAN(rrd):
	"""
	Stat class to measure load of the san fiber channels
	and report them to the rrd file
	"""
	def __init__(self):
		"""
		Main loop for the daemon
		"""
		self.hostname = socket.gethostname()
		self.fqdn = socket.getfqdn()
		if self.fqdn == 'localhost':
			self.fqdn = self.hostname
		self.rrd_dir = '/Volumes/discreet/lib/ganglia/rrds/%s' % self.fqdn
		self.sanfile_dir ="/Volumes/discreet/lib/ganglia/SAN_files"
		self.sector_size = 512

	def run(self):
		"""
		This method is called from the a52sd daemon.
		"""
		self.update_rrds()

	def create_rrds(self,dry_run=False):
		"""
		Create the concurrent user rrd file
		"""
		# check for the host directory:
		if not os.path.exists(self.rrd_dir):
			utils.makedirs(self.rrd_dir)

		self.find_sans()
		for stone,luns in self.sans.items():
			rrd_file = "%s/%s_%s.rrd" % (self.rrd_dir,self.hostname,stone.lower())
			if not os.path.exists(rrd_file):
				# rrdcreate = "rrdtool create --no-overwrite"
				# rrdtool on RHEL4 doesn't understand --no-overwrite
				rrdcreate = "rrdtool create"
				args = " %s" % (rrd_file)
				args+= " DS:bytes_read_L0:COUNTER:60:0:30000000000"
				args+= " DS:bytes_read_L1:COUNTER:60:0:30000000000"
				args+= " DS:bytes_written_L0:COUNTER:60:0:30000000000"
				args+= " DS:bytes_written_L1:COUNTER:60:0:30000000000"
				args+= " RRA:AVERAGE:0.5:12:2000" 
				command = rrdcreate+args
				print "COMMAND:",command
				if not dry_run:
					os.system(command)
		

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
#		self.sans = {	'SANSTONE01':["F6412SAS01L0","F6412SAS01L1"],
#					'SANSTONE02':["F6412SAS02L0","F6412SAS02L1"],
#					'SANSTONE03':["F6412SAS03L0","F6412SAS03L1"],
#					'SANSTONE04':["F6412SATA02L0","F6412SATA02L1"],
#					'SANSTONE05':["F5412SATA01L0","F5412SATA01L1"],
#					'SANSTONE06':["F5412SATA02L0","F5412SATA02L1"],
#					'SANSTONE07':["F6412SATA01L0","F6412SATA01L1"],
#					'SANSTONE08':["F6412SAS05L0","F6412SAS05L1"]}
		self.sans = {	'SANSTONE01':["F6412SAS01L0","F6412SAS01L1"],
					'SANSTONE02':["F6412SAS05L0","F6412SAS05L1"],
					'SANSTONE03':["F6412SAS04L0","F6412SAS04L1"],
					'SANSTONE04':["F6412SAS03L0","F6412SAS03L1"],
					'SANSTONE05':["F6412SAS02L0","F6412SAS02L1"],
					'SANSTONE06':["F5412SATA01L0","F5412SATA01L1"],
					'SANSTONE07':["F6500Rental01L0","F6500Rental01L1"]}
		self.luns = {}
		self.blkdevs = {}

		# open the host .san file and find each san's block devices
		sanfile = '%s/%s.san' % (self.sanfile_dir,self.hostname)
		if not os.path.exists(sanfile):
			print "Error: cannot find SAN file %s" % sanfile
			return None
		fl = open(sanfile)
		lines = fl.readlines()
		#regx = re.compile('.*(/dev/[a-z]*).*(".*")')
		_re = re.compile('.*(/dev/[a-z]*).*"(F[56]412.*)"')
		for line in lines:
			regx = re.match(_re,line)
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

	def update_rrds(self):
		"""
		Insert the current stats into the SAN rrds
		"""
		# find the sans on this host
		self.find_sans()
		# get the stats from the san's block devices
		self.get_stats()
		# form and execute the rrd commands
		for stone,luns in self.sans.items():
			lun0,lun1 = luns
			try:
				blkdev0 = self.luns[lun0]
				blkdev1 = self.luns[lun1]
				rrd_file = "%s/%s_%s.rrd" % (self.rrd_dir,self.hostname,stone.lower())
				if not os.path.exists(rrd_file):
					self.create_rrds()
				bytes_read0 = int(self.blkdevs[blkdev0]['sectors_read']) * self.sector_size
				bytes_read1 = int(self.blkdevs[blkdev1]['sectors_read']) * self.sector_size
				bytes_written0 = int(self.blkdevs[blkdev0]['sectors_written']) * self.sector_size
				bytes_written1 = int(self.blkdevs[blkdev1]['sectors_written']) * self.sector_size
				values = "%s:%s:%s:%s" % (bytes_read0,bytes_read1,bytes_written0,bytes_written1)
				#print "self.update_rrd(",rrd_file,'N',values
				self.update_rrd(rrd_file,'N',values)
			except: pass


if __name__ == "__main__":
	s = SAN()
	s.run()
#	s.find_sans()
#	s.create_san_rrds()
#	s.update_rrds()
	#s.update_san_rrds()



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
