#!/usr/bin/python

import warnings
warnings.filterwarnings("ignore",category=DeprecationWarning)
import time
import sys
import os
import popen2
import datetime
import commands
import socket
import logging, logging.handlers
sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import messenger
from A52.utils import fileutil
from A52.Framestore import Framestore
from select import select
try:
	from paramiko import *
except:pass

from optparse import OptionParser
p = OptionParser()
p.add_option("-H",dest='host', type='string',help="hostname (will backup all sanstones on that host")
p.add_option("-s",dest='sanstone', type='string',help="sanstone name")
p.add_option("-g",dest='exclude_globals', action='store_true',default=False,help="exclude global files")
p.add_option("-m",dest='exclude_media', action='store_true',default=False,help="exclude media cache")
p.add_option("-c",dest='exclude_clips', action='store_true',default=False,help="exclude clip directories")
p.add_option("-d",dest='dry_run', action='store_true',default=False,help="Dry run")
p.add_option("-x",dest='run_exec', action='store_true',default=False,help="Execute commands (default mode is 'list only')")
p.add_option("--sw",dest='sw_ctl', action='store_true',default=False,help="Stop / Start stone+wire. Warning: use carefully.")
p.add_option("-e",dest='email', action='store_true',default=False,help="Send email status")
p.add_option("--mount",dest='mount_stone', type='string',help="Mount a sanstone. Warning: this shuts down and reconfigures stone+wire.")
options,args = p.parse_args()

if options.sanstone: options.sanstone = options.sanstone.upper()

log = None
def datestamp():
	"""
	Simple format function for all datestamps
	that will show up in the logs.
	"""
	stamp = datetime.datetime.strftime(datetime.datetime.now(),'%b %d %H:%M:%S')
	#stamp = datetime.datetime.strftime(datetime.datetime.now(),'%a %b %d %H:%M:%S')
	return "[%s]" % (stamp)

class Log:


	def __init__(self,logfile='dl_mirror.log',logdir="/var/log/dl_mirror"):
		self.logdir = logdir
		self.logfile = logfile

	def create_log(logfile='dl_mirror.log',logdir="/var/log/dl_mirror"):
		#print "Creating log: %s/%s" % (logdir,logfile)
		# Create the log directory
		if not os.path.exists(logdir):
			os.makedirs(logdir)
			os.chmod(logdir, 0755)
	
		# Create the logger
		log = logging.getLogger('DL_MIRROR')
	
		# File handler
		# Keep 10 log files in the folder.
		log_handler = logging.handlers.RotatingFileHandler("%s/%s" % (logdir,logfile), 'a', 20000000, 10)
		log_format = logging.Formatter('[%(asctime)s] %(lineno)s %(message)s','%b %d %H:%M:%S')
		log_handler.setFormatter(log_format)
		log.addHandler(log_handler)
		# Check if we need to rotate the log file
		#if os.path.exists(logfile):
		#	fhand.doRollover()
		#os.chmod(logFile, 0666)
	
		# Stream handler
		stream_handler = logging.StreamHandler(sys.stdout)
		stream_format = logging.Formatter('%(message)s')
		stream_handler.setFormatter(stream_format)
		log.addHandler(stream_handler)
		#if os.getenv("DL_INSTALL_DEBUG"):
		#	stream_handler.setLevel(logging.DEBUG)
		#else:
		#	stream_handler.setLevel(logging.INFO)
	
		stream_handler.setLevel(logging.ERROR)
		log_handler.setLevel(logging.INFO)
		log.setLevel(logging.DEBUG)
		return log
	create_log = staticmethod(create_log)
	
	def create_rsync_log(logfile='dl_mirror.log',logdir="/var/log/dl_mirror"):
		# Create the log directory
		if not os.path.exists(logdir):
			os.makedirs(logdir)
			os.chmod(logdir, 0755)
	
		# Create the logger
		rsync_log = logging.getLogger('DL_MIRROR_RSYNC')
	
		# File handler
		# Keep 10 log files in the folder.
		rsync_log.abs_logfile = "%s/%s" % (logdir,logfile)
		log_handler = logging.handlers.RotatingFileHandler("%s/%s" % (logdir,logfile), 'a', 500000, 10)
		log_format = logging.Formatter('[%(asctime)s] %(message)s','%b %d %H:%M:%S')
		log_handler.setFormatter(log_format)
		rsync_log.addHandler(log_handler)
	
		log_handler.setLevel(logging.INFO)
		rsync_log.setLevel(logging.INFO)
		return rsync_log
	create_rsync_log = staticmethod(create_rsync_log)
	
class RsyncException(Exception):
	"""
	Rsync Exception class to single out
	specificly when rsync errors out.
	"""
	pass

class Command:


	def __init__(self,name,command):
		self.name = name
		self.command = command
		self.start_time = None
		self.stop_time = None
	
	def rsync(self):
		"""
		rsync handler:
			- checks for the dry_run flag
			- handles log entries
			- handles errors and notifications
		"""
		if options.dry_run:
			_command = "%s -n" % (self.command)
		else:
			_command = self.command

		self.start_time = datetime.datetime.now()
		start_message = "[44mSTART[m: %s" % (_command)
		rsync_log.info(start_message)
		print "\t\t%s" % (_command)

		if options.run_exec:
			try:
				self._rsync(_command)
			except RsyncException,error:
				from_addr = 'conform01@a52.com'
				to_addrs = 'eng@a52.com'
				#to_addrs = 'tommy.hooper@a52.com'
				subject = "Framestore mirror error"
				msg = "Error received from rsync:\n"
				msg+= "Command: %s\n" % _command
				msg+= "Logfile: %s\n" % rsync_log.abs_logfile
				# grab the end of the logfile to 
				# put in the email
				#rsync_log.flush()
				tail = commands.getoutput('tail %s' % rsync_log.abs_logfile)
				msg+= "\nTail of logfile...\n"
				msg+= tail
				messenger.Email(from_addr,to_addrs,subject,msg)
	
		self.stop_time = datetime.datetime.now()
		delta = self.stop_time - self.start_time
		stop_msg = "[41mSTOP[m: (%s: elapsed) : %s" % (delta,_command)
		rsync_log.info(stop_msg)

	def _rsync(self,command):
		"""
		Spawn the rsync 'command' in 
		a pipe. This routine is separated
		so it can raise exceptions on errors
		to be dealth with by the spawning
		function.
		"""
		# spawn the command in a subprocess and wait for it to exit. 
		job = popen2.Popen4(command,0)
		while job.poll() == -1:
			# capture the output of the command
			# for this command it's not necessary
			# to show the output
			sel = select([job.fromchild], [], [], 0.05)
			if job.fromchild in sel[0]:
				output = os.read(job.fromchild.fileno(), 16384)
				msg = output.strip()
				for line in msg.split('\n'):
					rsync_log.info(line)
			time.sleep(0.01)
	
		# flush any possible info stuck in the buffer
		while output != '':
			output = os.read(job.fromchild.fileno(), 16384)
			msg = "%s" % (output.strip())
			rsync_log.info(msg)
	
		if job.poll():
			# got an error status back
			error = "%s" % job.poll()
			rsync_log.error(error)
			raise RsyncException,error


class Queue:


	def __init__(self):
		pass

	def __getattr__(self,name):
		if name == 'commands':
			self.commands = {}
			return self.commands
		message = "Queue object has no attribute '%s'" % (name)
		raise AttributeError,message
	
	def add_cmd(self,qtype,name,command):
		if not self.commands.has_key(qtype):
			self.commands[qtype] = []
		self.commands[qtype].append(Command(name,command))

	def show_commands(self):
		for cmd in self.commands:
			print cmd.command

	def run_queue(self,qtype):
		swdb = False
		swdb_locked = False
		events = []
		if not self.commands.has_key(qtype):
			print "\t\tNo commands queued"
			return []

		# form a dictionary of commands
		# so we can handle the swdb specifically
		run_list = []
		for command in self.commands[qtype]:
			if command.name == 'swdb':
				swdb = command
			elif command.name == 'swdb_locked':
				swdb_locked = command
			else:
				if qtype == 'media':
					if stone.is_mount():
						run_list.append(command)
				else:	# qtype here is 'clip'
					run_list.append(command)
			
		if swdb:
			if host.stone_wire('stop'):
				log.info(swdb.command)
				#events.append(swdb.command)
				swdb.rsync()
				elapsed = swdb.stop_time-swdb.start_time
				events.append(elapsed)
				cmp_msg = " -- Done. Elapsed time: %s" % (elapsed)
				log.info(cmp_msg)
				# restart the stone+wire
				host.stone_wire('start')
			else:
				run_list.append(swdb_locked)
			
		for command in run_list:
			log.info(command.command)
			#events.append(command.command)
			command.rsync()
			elapsed = command.stop_time-command.start_time
			events.append(elapsed)
			cmp_msg = " -- Done. Elapsed time: %s" % (elapsed)
			log.info(cmp_msg)
		return events

	def summary_message(self):
		msg = ""
		for cmd in self.commands:
			if cmd.start_time:
				msg+= "%s\n" % cmd.command
				msg+= "Start: %s\n" % cmd.start_time
				msg+= "Stop: %s\n" % cmd.stop_time
				msg+= "Elapsed: %s\n" % (cmd.stop_time - cmd.start_time)
		return msg

class Host(Queue):


	def __init__(self,host):
		self.host = host
		self.name = host
		self.generate_queue()
		self.rsync_log = Log.create_rsync_log(logfile="%s_mirror.log" % self.host)
	
	def generate_queue(self):
		"""
		Return a list of rsync commands that will backup
		all the global stone+wire files (not specific
		to any single framestore).
		"""
		mirror_path = '/Volumes/stonemirror/%s' % (self.host)
		automount_path = '/hosts/%s/usr' % (self.host)
		self.add_cmd('global','project','rsync -av --delete %s/discreet/project/project.* %s/project/' % (automount_path,mirror_path))
		self.add_cmd('global','user_effects','rsync -av --delete %s/discreet/user/effects/user.* %s/user/effects/' % (automount_path,mirror_path))
		self.add_cmd('global','user_editing','rsync -av --delete %s/discreet/user/editing/user.* %s/user/editing/' % (automount_path,mirror_path))
		self.add_cmd('global','sw_cfg','rsync -av --delete %s/discreet/sw/cfg %s/sw/' % (automount_path,mirror_path))
		self.add_cmd('global','sw_depend','rsync -av --delete %s/discreet/sw/sw_depend %s/sw/' % (automount_path,mirror_path))
		self.add_cmd('global','swdb','rsync -av --delete %s/discreet/sw/swdb %s/sw/' % (automount_path,mirror_path))
		self.add_cmd('global','swdb_locked','rsync -av --delete %s/discreet/sw/swdb/ %s/sw/swdb_locked/' % (automount_path,mirror_path))

	def is_locked(self):
		m = Mirror()
		for stone in m.stones:
			if stone.host== self.name:
				if stone.is_locked():
					return True
		return False

	def stone_wire(self,action):
		"""
		start / stop stone+wire
		"""
		if not options.sw_ctl:
			log.info("Stone and wire control not set (--sw). Will not try to %s stone+wire." % (action))
			return False
		if self.is_locked():
			message = "WARNING: %s is locked. Cannot shut down stone+wire" % (self.host)
			log.info(message)
			print "\t\t[41m%s[m" % (message)
			log.info("Host is locked. Will not try to %s stone+wire." % (action))
			if options.email:
				subject = "DL Mirror Warning: Could not %s stone+wire" % (action)
				messenger.Email(from_addr,to_addrs,subject,message)
			return False

		if action == 'start':
			message = "Starting up stone+wire on %s" % (self.host)
			log.info(message)
			print "\t\t%s" % message
			# startup stone+wire 
			_out,_err = self._cmd('/etc/init.d/stone+wire start')
		elif action == 'stop':
			message = "Shutting down stone+wire on %s" % (self.host)
			log.info(message)
			print "\t\t%s" % message
			# shutdown stone+wire 
			_out,_err = self._cmd('/etc/init.d/stone+wire stop')
			#_out,_err = self._cmd('date')

		if _err:
			message = "ERROR starting / stopping stone+wire on %s" % (self.host)
			print "\t\t%s" % message
			log.info(message)
			if options.email:
				subject = "DL Mirror Error starting / stopping stone+wire on %s" % (self.host)
				messenger.Email(from_addr,to_addrs,subject,message)
			return False
		return True

	def _cmd(self,command):
		"""
		Execute 'command'.
		If self.host is not the current host 
		then use ssh.
		"""
		if self.host == socket.gethostname():
			_err,_out = commands.getstatusoutput(command)
			return (_out,_err)
		else:
			command = "ls /tmpx"
			ssh_command = "ssh -t %s@%s %s" % ('root',self.host,command)
			status,_out = commands.getstatusoutput(ssh_command)
			return (_out,status)

			# I could probably use this method to
			# run the ssh command but it's a little
			# overcomplicated for little gain.
			#ssh = SSHClient()
			#ssh.load_system_host_keys()
			#ssh.connect(self.host,username='root')
			#channel = ssh.invoke_shell() 
			#channel.settimeout(5)
			#channel.sendall('ls /tmp')
			#stdout = ''
			#expect = "some line we're looking for"
			#while True:
			#	try:
			#		stdout += channel.recv(1024)
			#		if stdout.endswith(expect):
			#			break
			#	except socket.timeout:
			#		print "TIMEOUT"
			#		break
			#print "STDOUT:",stdout
			#return(stdout,stdout)


			# this doesn't work for some hosts
			# since the stone+wire restart 
			# latches onto the tty
			#ssh.connect(self.host,username='root')
			#_in,_out,_err = ssh.exec_command(command)
			#stdout = _out.readlines()
			#stderr = _err.readlines()
			#return (stdout,stderr)

class Sanstone(Queue):


	def __init__(self,name,host,volume,mount,hostdir,partition,partition_dir):
		self.name = name
		self.host = host
		self.volume = volume
		self.mount = mount
		self.hostdir = hostdir
		self.partition = partition
		self.partition_dir = partition_dir
		self.queue = []
		self.mirror_path = '/Volumes/stonemirror/%s' % (self.host)
		self.automount_path = '/hosts/%s/usr' % (self.host)
		self.full_pdir = "%s/%s" % (self.hostdir,self.partition_dir)
		self.generate_queue()

	def generate_queue(self):
		"""
		Return a list of rsync commands that will backup
		the /usr/discreet/clip/stonefs<#> directories
		and the specific stone+wire files for a single framestore
		"""
		self.add_cmd('clip','clip','rsync -av --delete %s/discreet/clip/%s %s/clip/' % 
			(self.automount_path,self.volume,self.mirror_path))
		mount_point = "/Volumes/%s" % (self.mount)
		if os.path.ismount(mount_point):
			self.add_cmd('media','media','rsync -av --delete /Volumes/%s/%s/ %s/media/%s/' % 
				(self.mount,self.full_pdir,self.mirror_path,self.partition_dir))
		else:
			log.error("Error: Media cache is not mounted! Mount point: %s" % mount_point)

	def flush_swdb(self):
		"""
		Shut down the sw_dbd so the database is flushed to 
		disk before we back it up.
		"""
		# have to check for possible connections
		fs = Framestore(host=self.host,volume=self.volume)
		if fs.is_locked():
			log.error("\n[41m%s:%s is not LOCKED[m\n" % (self.host,self.volume))
			#fs.show_locks()
			# let's see if the process exists
			for hexid,info in fs.locks.iteritems():
				if info['count'] >= 1:
					pid = int(str(info['pid']).lstrip('0'))
					host = info['host']
		else:
			log.error("\n[42m%s:%s is not locked[m\n" % (self.host,self.volume))
			# shutdown stone+wire 
			ssh = SSHClient()
			ssh.load_system_host_keys()
			#ssh.connect(self.host,username='root')
			ssh.connect('burn01',username='root')
			_in,_out,_err = ssh.exec_command('hostname')
			for line in _out.readlines():
				print line.strip()
			return

	def is_locked(self):
		fs = Framestore(host=self.host,volume=self.volume)
		return fs.is_locked()

	def is_mount(self):
		path = "/Volumes/%s" % self.mount
		if os.path.ismount(path):
			return True
		return False
		

	def mount_mirror(self,unmount=False):
		"""
		Shut down stone+wire and reconfigure to mount
		or unmount the mirror framestore.
		"""
		# shut down stone+wire
		hst = Host(socket.gethostname())
		hst.stone_wire('stop')

		# /usr/discreet/project
		self._link_project_dir(unmount=unmount)

		# /usr/discreet/user
		self._link_user_dir(unmount=unmount)

		# /usr/discreet/sw/cfg/stone+wire.cfg
		self._create_sw_cfg(unmount=unmount)

		# /usr/discreet/sw/swdb
		self._link_swdb(unmount=unmount)

		# /usr/discreet/clip/stonefs(X)
		self._link_clip_dirs(unmount=unmount)

		# /usr/discreet/sw/cfg/sw_framestore_map
		self._create_sw_framestore_map(unmount=unmount)

		# /usr/discreet/sw/cfg/sw_storage.cfg
		self._link_sw_storage_cfg(unmount=unmount)

		# start up stone+wire
		hst.stone_wire('start')

	def _link_media_cache(self,unmount=False):
		"""
		Link or unlink the media cache
		directory for the mirror
		"""
		mc = '/Volumes/%s/%s' % (self.mount,self.full_pdir)
		mirror_mc = '%s/media/%s' % (self.mirror_path,self.partition_dir)
#		if unmount:
#			if fileutil.islink(mc):
#				os.remove(mc)
#			if fileutil.exists("%s.orig_dlm" % mc):
#				os.rename("%s.orig_dlm" % mc,mc)
#		else:
#			fileutil.symlink(mirror_mc,mc,archive_tag='orig_dlm')

	def _link_clip_dirs(self,unmount=False):
		"""
		Link or unlink the /usr/discreet/clip
		directories for the mirror
		"""
		if not os.path.exists('/usr/discreet/clip'):
			os.mkdir('/usr/discreet/clip')
		prt = "/usr/discreet/clip/stonefs%s" % self.partition
		mirror_prt = "%s/clip/stonefs%s" % (self.mirror_path,self.partition)
	
		if unmount:
			if fileutil.exists(prt) and fileutil.islink(prt):
				os.remove(prt)
			if fileutil.exists("%s.orig_dlm" % prt):
				os.rename("%s.orig_dlm" % prt,prt)
		else:
			fileutil.symlink(mirror_prt,prt,archive_tag='orig_dlm')

	def _link_project_dir(self,unmount=True):
		"""
		Link or unlink the /usr/discreet/project directory
		to the mirror
		"""
		# /usr/discreet/project
		udp = '/usr/discreet/project'
		udp_target = "%s/project" % self.mirror_path
		if unmount:
			if fileutil.exists(udp) and fileutil.islink(udp):
				os.remove(udp)
			if fileutil.exists("%s.orig_dlm" % udp):
				os.rename("%s.orig_dlm" % udp,udp)
		else:
			fileutil.symlink(udp_target,udp,archive_tag='orig_dlm')

	def _link_user_dir(self,unmount=True):
		"""
		Link or unlink the /usr/discreet/user directory
		to the mirror
		"""
		udu = '/usr/discreet/user'
		udu_target = "%s/user" % self.mirror_path
		if unmount:
			if fileutil.islink(udu):
				os.remove(udu)
			if fileutil.exists("%s.orig_dlm" % udu):
				os.rename("%s.orig_dlm" % udu,udu)
		else:
			# /usr/discreet/user
			fileutil.symlink(udu_target,udu,archive_tag='orig_dlm')


	def _link_sw_storage_cfg(self,unmount=True):
		"""
		Link or unlink the sw_storage.cfg 
		to the mirror
		"""
		cfg = '/usr/discreet/sw/cfg/sw_storage.cfg'
		cfg_target = "%s/sw/cfg/sw_storage.cfg" % self.mirror_path
		if unmount:
			if fileutil.islink(cfg):
				os.remove(cfg)
			if fileutil.exists("%s.orig_dlm" % cfg):
				os.rename("%s.orig_dlm" % cfg,cfg)
		else:
			fileutil.symlink(cfg_target,cfg,archive_tag='orig_dlm')


	def _create_sw_cfg(self,unmount=False):
		"""
		Create a custom stone+wire.cfg file
		for mounting this framestore.

		TODO: These lines are probably not 
		necessary in the cfg but need to test:

		 [DefaultFileFormats]
		 [MetadataDirectory]
		 [StandardFSMediaOptions]
		 [Initialization]

		"""
		# check the existing stone+wire.cfg
		# for the DL_MIRROR tag in the file.
		# if it's not there move it aside to be safe
		cfg = '/usr/discreet/sw/cfg/stone+wire.cfg'
		if os.path.exists(cfg):
			# look for the DL_MIRROR
			f = open(cfg)
			for line in f.readlines():
				if 'DL_MIRROR' in line:
					f.close()
					os.remove(cfg)
					break

		if os.path.exists(cfg):
			# move the original file aside
			os.rename(cfg,"%s.orig_dlm" % cfg)

		if unmount:
			# move the original back
			os.rename("%s.orig_dlm" % cfg,cfg)
		else:
			# write the new cfg	
			n = open(cfg,'w')
			n.write("# DL_MIRROR: Auto-generated %s\n" % cfg)
			n.write("# Original cfg moved to %s.orig_dlm\n" % cfg)
			n.write("[Partition%s]\n" % self.partition)
			n.write("Name=%s\n" % self.name)
			n.write("Path=%s/media/%s\n" % (self.mirror_path,self.partition_dir))
			n.write("Shared=True\n")
			n.close()

	def _create_sw_framestore_map(self,unmount=False):
		"""
		Create a custom stone+wire.cfg file
		for mounting this framestore.

		FRAMESTORE=smoke01	HADDR=192.168.97.201				ID=201

		"""
		# check the existing sw_framestore_map
		# for the DL_MIRROR tag in the file.
		# if it's not there move it aside to be safe
		cfg = '/usr/discreet/sw/cfg/sw_framestore_map'
		mirror_cfg = '%s/sw/cfg/sw_framestore_map' % self.mirror_path
		# get the version # and the ID 
		# out of the mirror's sw_framestore_map
		f = open(mirror_cfg)
		for line in f.readlines():
			if "VERSION" in line:
				version = line.strip().split('=')[1].strip()
			if self.host in line:
				ID = line.strip().split('ID=')[1].strip()
			if "INTERFACES" in line:
				break
		f.close()

		if os.path.exists(cfg):
			# look for the DL_MIRROR
			f = open(cfg)
			for line in f.readlines():
				if 'DL_MIRROR' in line:
					f.close()
					os.remove(cfg)
					break

		if os.path.exists(cfg):
			# move the original file aside
			os.rename(cfg,"%s.orig_dlm" % cfg)

		if unmount:
			# move the original back
			if fileutil.exists("%s.orig_dlm" % cfg):
				os.rename("%s.orig_dlm" % cfg,cfg)
		else:
			# write the new cfg	
			n = open(cfg,'w')
			n.write("# DL_MIRROR: Auto-generated %s\n" % cfg)
			n.write("# Original cfg moved to %s.orig_dlm\n" % cfg)
			n.write("VERSION=%s\n" % version)
			n.write("[FRAMESTORES]\n")
			n.write("FRAMESTORE=%s\tHADDR=localhost\tID=%s\n\n" % (socket.gethostname(),ID))
			n.write("[INTERFACES]\n")
			n.close()

	def _link_swdb(self,unmount=False):
		"""
		Swap the swdb files for this framestore.
		"""
		# check if sw_dbd is running before we do anything
		command = "ps -C sw_dbd -o pid="
		pid = commands.getoutput(command).strip()
		if pid:
			log.error("WARNING: sw_dbd is still running")
			#return False

		if not os.path.exists('/usr/discreet/sw/swdb'):
			os.mkdir('/usr/discreet/sw/swdb')
		db = '/usr/discreet/sw/swdb/part%s.db' % self.partition
		db_link = '%s/sw/swdb/part%s.db' % (self.mirror_path,self.partition)
		count = '/usr/discreet/sw/swdb/part%s.count' % self.partition
		count_link = '%s/sw/swdb/part%s.count' % (self.mirror_path,self.partition)

		if fileutil.exists(db) and fileutil.islink(db):
			os.remove(db)
		elif os.path.exists(db):
			os.rename(db,"%s.orig_dlm" % db)

		if fileutil.exists(count) and fileutil.islink(count):
			os.remove(count)
		elif os.path.exists(count):
			os.rename(count,"%s.orig_dlm" % count)

		if unmount:
			# move the originals back
			if os.path.exists("%s.orig_dlm" % db):
				os.rename("%s.orig_dlm" % db,db)
			if os.path.exists("%s.orig_dlm" % count):
				os.rename("%s.orig_dlm" % count,count)
		else:
			os.symlink(db_link,db)
			os.symlink(count_link,count)

class Mirror:


	def __init__(self,host=None,sanstone=None):
#		global log
		self.log = Log.create_log()
		log = self.log
		self.stones = []
		self._get_stones(sanstone=sanstone,host=host)
		self._get_hosts(host=host)
		self.mirror_path = '/Volumes/stonemirror'
		if not self.is_mount():
			message = "ERROR: Mirror location is not a mounted volume"
			log.error(message)
			raise Exception,message

	def _get_stones(self,sanstone=None,host=None):
		"""
		Returns a dictionary of all the sanstones
		that need to be mirrored. This list could be 
		pulled from the database, however we want to 
		make this script not reliant on the db.
		"""
		# define the sans we're mirroring
		# NOTE: 
		#	- 'hostdir' exists for the not-so-correct 'flame3' directory 
		#	- 'partition_dir' is used to specifically target a single
		#	  media cache directory.
		stones = {	'SANSTONE01':{	'host':'flame01',
							'volume':'stonefs4',
							'mount':'F6412SAS01',
							'hostdir':'flame01',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE02':{	'host':'flame02',
							'volume':'stonefs4',
							'mount':'F6412SAS05',
							'hostdir':'flame02',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE03':{	'host':'flame03',
							'volume':'stonefs4',
							'mount':'F6412SAS04',
							'hostdir':'flame3',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE04':{	'host':'flame04',
							'volume':'stonefs4',
							'mount':'F6412SAS03',
							'hostdir':'flame04',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE05':{	'host':'smoke01',
							'volume':'stonefs4',
							'mount':'F6412SAS02',
							'hostdir':'smoke01',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE06':{	'host':'smack01',
							'volume':'stonefs4',
							'mount':'F5412SATA01',
							'hostdir':'smack01',
							'partition':'4',
							'partition_dir':'p4'},
				'SANSTONE07':{	'host':'smoke01',
							'volume':'stonefs5',
							'mount':'F6500Rental01',
							'hostdir':'smoke01',
							'partition':'5',
							'partition_dir':'p5'},
				#'SANSTONE08':{	'host':'conform01',
				#			'volume':'stonefs4',
				#			'mount':'F5412SATA02',
				#			'hostdir':'conform01',
				#			'partition':'4',
				#			'partition_dir':'p4'},
				'SANSTONE09':{	'host':'flame02',
							'volume':'stonefs5',
							'mount':'F6500Rental02',
							'hostdir':'flame02',
							'partition':'5',
							'partition_dir':'p5'},
				'SANSTONE10':{	'host':'flame01',
							'volume':'stonefs5',
							'mount':'F6500SAS02',
							'hostdir':'flame01',
							'partition':'5',
							'partition_dir':'p5'}}
	
		# if a specific stone was passed
		# as an arguement, limit the list
		# of stones
		if sanstone:
			if stones.has_key(sanstone):
				stones = {sanstone:stones[sanstone]}
			else:
				message = "Unknown sanstone: %s" % sanstone
				log.error(message)
				raise Exception,message

		# if a specific host was passed
		# weed out the stones that do not 
		# belong to that host
		for name,info in stones.iteritems():
			if not host or host == info['host']:
				obj = Sanstone(	name=name,
							host=info['host'],
							volume=info['volume'],
							mount=info['mount'],
							hostdir=info['hostdir'],
							partition=info['partition'],
							partition_dir=info['partition_dir'])
				self.stones.append(obj)

	def _get_hosts(self,host=None):
		"""
		Generate a list of hosts from the
		'stone' dictionary generated by the
		get_stones function.
		"""
		hostlist = []
		self.hosts = []
		for stone in self.stones:
			if host and stone.host == host:
				self.hosts.append(Host(stone.host))
			elif not host and not stone.host in hostlist:
				self.hosts.append(Host(stone.host))
				hostlist.append(stone.host)

	def setup_mirror(self):
		"""
		Create the directories necessary for 
		our rsync.
		"""
		for stone in self.stones:
			mirror_path = '%s/%s' % (self.mirror_path,stone.host)
			try:
				os.makedirs('%s' % (mirror_path))
			except:pass
			try:
				os.makedirs('%s/user/' % (mirror_path))
			except:pass
			try:
				os.makedirs('%s/media' % (mirror_path))
			except:pass

	def is_mount(self):
		if os.path.ismount(self.mirror_path):
			return True
		return False


if __name__ == '__main__':

	from_addr = 'conform01@a52.com'
	to_addrs = 'eng@a52.com'
	#to_addrs = 'tommy.hooper@a52.com'

	# get a mirror object which will
	# contain all the sanstones
	m = Mirror(host=options.host,sanstone=options.sanstone)

	#TODO: mounting / unmounting routine here:
#	if options.mount_stone:
#		print options.mount_stone
###	if socket.gethostname() == 'conform01':
#		for s in m.stones:
#			if s.name.lower() == options.mount_stone.lower():
#				mount_stone = s
#		print mount_stone.name
#		mount_stone.mount_mirror(unmount=True)
##		s = m.stones[6]
##		print s.name
###		stone.mount_mirror()
###		s.mount_mirror(unmount=True)
#		sys.exit()

	m.setup_mirror()

	print "\n\nStarting Mirror...\n"
	log.info("------------------------- Starting Mirror -------------------------")
	#
	#  GLOBAL FILES
	#
	if not options.exclude_globals:
		#print "[44m%-20s[m" % ("Global Files:")
		print "%-20s" % ("Global Files:")
		events = ["Global File rsync elapsed times:"]
		for host in m.hosts:
			rsync_log = host.rsync_log
			print "\t %s:" % (host.name)
			log.info("Syncing global files for %s" % host.name)
			start_time = datetime.datetime.now()
			host.run_queue('global')
			stop_time = datetime.datetime.now()
			events.append("%s: %s" % (host.name,stop_time-start_time))
		if options.email:
			msg = "\n".join(events)
			subject = "DL Mirror : Global Files"
			messenger.Email(from_addr,to_addrs,subject,msg)
	#
	#  CLIP DIRECTORIES
	#
	if not options.exclude_clips:
		#print "[44m%-20s[m" % ("Clip Directories:")
		print "%-20s" % ("Clip Directories:")
		events = ["Clip Directory elapsed times:"]
		for stone in m.stones:
			host = Host(stone.host)
			rsync_log = host.rsync_log
			log.info("Syncing clip directories for %s (%s)" % (stone.name,stone.host))
			print "\t %s:%s" % (stone.host,stone.name)
			start_time = datetime.datetime.now()
			stone.run_queue('clip')
			stop_time = datetime.datetime.now()
			events.append("%s (%s): %s" % (stone.name,stone.host,stop_time-start_time))
		if options.email:
			msg = "\n".join(events)
			subject = "DL Mirror : Clip Directories"
			messenger.Email(from_addr,to_addrs,subject,msg)
	#
	#  MEDIA CACHES
	#
	if not options.exclude_media:
		#print "[44m%-20s[m" % ("Media Caches")
		print "%-20s" % ("Media Caches:")
		events = ["Media Cache elapsed times:"]
		for stone in m.stones:
			host = Host(stone.host)
			rsync_log = host.rsync_log
			log.info("Syncing media caches for %s (%s)" % (stone.name,stone.host))
			print "\t %s:%s" % (stone.host,stone.name)
			start_time = datetime.datetime.now()
			stone.run_queue('media')
			stop_time = datetime.datetime.now()
			events.append("%s (%s): %s" % (stone.name,stone.host,stop_time-start_time))

		if options.email:
			msg = "\n".join(events)
			# send the status email
			subject = "DL Mirror : Media Cache"
			messenger.Email(from_addr,to_addrs,subject,msg)

	# finish up
	log.info("------------------------- Mirror Complete -------------------------")






