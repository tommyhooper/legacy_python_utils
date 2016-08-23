from A52.utils import dateutil
from A52.utils import print_array
import os,time,sys,threading,signal,re,bz2
import popen2 # Deprecated ./fuse_2011.py:5: DeprecationWarning: The popen2 module is deprecated.  Use the subprocess module.
import select as Select

class rsync_thread(object):
	def __init__(self,command,logfile=None,verbose=False):
		self.running = False
		self.verbose = verbose
		self.command = command
		self.progress = {	'current_file':None,
					'bytes_copied':0,
					'percent_done':'0%',
					'transfer_rate':'0MB/s',
					'est_remain':'0.00:00',
					'xfer_num':0,
					'xfer_remain':0,
					'xfer_total':0}
		self.regx = {	'file_line':re.compile('^(.*)'),
					'xfer_line':re.compile('^.*%.*:??:.*$'),
					'xfer_num':re.compile('^.*#([0-9]+),.*$'),
					'xfer_remain':re.compile('^.*[^0-9]([0-9]+)/([0-9]+).*$')}
		self.logfile = logfile
		# open the logfile
		self.log = open(self.logfile,'a')

	def __del__(self):
		"""
		Cleanup on exit
		"""
		#print "Closing logfile"
		self.log.close()

	def start(self):
		#print "Starting rsync thread"
		threading.Thread(target=self._start).start()
		self.running = True

	def stop(self):
		#print "Stopping rsync thread"
		self._stopped = True

	def status(self):
		return self.progress

	def _start(self):
		"""
		Start method
		"""
		self._stopped = False
		# loop
		# spawn the command in a subprocess and wait for it to
		# exit. Keep flushing the gtk events so we can still
		# use the interface
		job = popen2.Popen4(self.command,0)
		while job.poll() == -1:
			# capture the output of the command
			# for this command it's not necessary
			# to show the output
			sel = Select.select([job.fromchild], [], [], 0.05)
			if job.fromchild in sel[0]:
				output = os.read(job.fromchild.fileno(), 16384),
				self.update_progress(output)
				#print progress
				#sys.stdout.flush()
			if self._stopped:
				os.kill(job.pid,signal.SIGTERM)
				break
			time.sleep(0.01)

		# mark that we're no longer running
		self.running = False
		# flush any possible info stuck in the buffer
		output = os.read(job.fromchild.fileno(), 16384)
		self.update_progress(output)
		#print output
		#sys.stdout.flush()
		if job.poll():
			pass
			# got an error status bac
			#print "\n>>> Caught Error: %s\n" % job.poll()
		else:
			pass
			# inferno exited normally
			#print "\n>>> Normal Exit: %s\n" % job.poll()

	def update_progress(self,output):
		"""
		Parse the output of the rsync command
		and update the progress
		"""
		if type(output) is tuple:
			lines = output[0]
		elif type(output) is str:
			lines = output
		else:
			print "\n\nWARNING: output is neither tuple or str\n\n"
			raise Exception

		for line in lines.split('\n'):
			if self.verbose:
				print line
			if len(line) > 0:
				# test if this line is a progress line
				if re.search(self.regx['xfer_line'],line):
					split = line.split()
					#print "SPLIT:%s:%s" % (len(split),split)
					self.progress['bytes_copied'] = split[0]
					self.progress['percent_done'] = split[1]
					self.progress['transfer_rate'] = split[2]
					self.progress['est_remain'] = split[3]
					# if this is a last line
					if len(split) == 6:
						regx = re.search(self.regx['xfer_num'],split[4])
						if regx:
							self.progress['xfer_num'] = regx.group(1)
						regx = re.search(self.regx['xfer_remain'],split[5])
						if regx:
							self.progress['xfer_remain'] = regx.group(1)
							self.progress['xfer_total'] = regx.group(2)
					elif len(split) == 10:
						#print "SPLIT 8:",split[8]
						regx = re.search(self.regx['xfer_num'],split[8])
						if regx:
							self.progress['xfer_num'] = regx.group(1)
						#print "SPLIT 9:",split[9]
						regx = re.search(self.regx['xfer_remain'],split[9])
						if regx:
							self.progress['xfer_remain'] = regx.group(1)
							self.progress['xfer_total'] = regx.group(2)
				else:
					self.progress['current_file'] = line
					#regx = re.search(self.regx['file_line'],line)
					#if regx:
					#	self.progress['current_file'] = regx.group(1)
					# write the file line to the logfile
					self.log.write("%s\n" % line)
					self.log.flush()

class Rsync:
	"""
	Wrapper class for the rsync_thread class.
	Spawns an rsync in a thread then loops updating
	the status every 'x' seconds
	"""
	def __init__(self,source,destination,logfile='/tmp/rsync_log',dry_run=False,log_message=None,delete=False,verbose=False):
		self.source = source
		self.destination = destination
		self.dry_run = dry_run
		self.delete = delete
		self.log_message = log_message
		self.logfile = logfile
		self.verbose = verbose
		self.progress_file = "%s.prog" % (os.path.splitext(self.logfile)[0])
		self.form_command()
		self.init_logfile()

	def form_command(self):
		if self.delete:
			delete = "--delete"
		else:
			delete = ""
			
		if self.dry_run:
			self.command = "rsync -avn %s %s %s" % (delete,self.source,self.destination)
		else:
			if self.verbose:
				self.command = "rsync -avn --progress %s %s %s" % (delete,self.source,self.destination)
			else:
				self.command = "rsync -an --progress %s %s %s" % (delete,self.source,self.destination)
			#self.command = "rsync -a --progress --out-format='%%n' %s %s" % (self.source,self.destination)

	def rsync(self):
		self.thread = rsync_thread(self.command,logfile=self.logfile,verbose=self.verbose)
		self.thread.start()
		while self.thread.running:
			self.status()
			time.sleep(1)
		self.thread.stop()

	def status(self):
		"""
		Get the status from the rsync thread and put it
		in the progress file
		"""
		status = self.thread.status()
#		print_array(status)
		message = ["------ RSYNC PROGRESS ------ "]
		if self.log_message:
			message.append(self.log_message)
		message.append("Current file: %s" % status['current_file'])
		message.append("\tBytes Copied: %s" % status['bytes_copied'])
		message.append("\tPercent Done: %s" % status['percent_done'])
		message.append("\tTransfer Rate: %s" % status['transfer_rate'])
		message.append("\tTime Remaining: %s" % status['est_remain'])
		message.append("\tTransfer Number: %s" % status['xfer_num'])
		message.append("\tTransfers Remaining: %s" % status['xfer_remain'])
		message.append("\tTransfers Total: %s" % status['xfer_total'])
		message.append("\t----------------------------------")
		try:
			overall_percent = int(round((int(status['xfer_num'])*1.0)/int(status['xfer_total']),2)*100)
		except: overall_percent = 0
		message.append("\tTotal Rsync done: %s%%\n" % overall_percent)
		p = open(self.progress_file,'w+',0)
		for line in message:
			#print line
			p.write("%s\n" % line)
		p.flush()
		p.close()

	def init_logfile(self):
		"""
		Make sure we can create and write to the logfile
		"""
		if os.path.exists(self.logfile):
			# move the logfile aside and compress it
			bz_file = bz2.BZ2File("%s.bz2" % self.logfile,'w')
			log = open(self.logfile,'r')
			bz_file.writelines(log.readlines())
			log.close()
			bz_file.close()
		#print "Logging output to %s" % self.logfile
		date = dateutil.get_datetime()
		time = dateutil.get_datetime(1)
		new_file = open(self.logfile,'w')
		new_file.write("#------------------------- RSYNC LOG -------------------------\n#\n")
		new_file.write("#%12s: %s\n" % ('Date',date))
		new_file.write("#%12s: %s\n" % ('Time',time))
		new_file.write("#%12s: %s\n" % ('Source',self.source))
		new_file.write("#%12s: %s\n" % ('Destination',self.destination))
		new_file.write("#%12s: %s\n" % ('Command',self.command))
		new_file.write("#%12s: %s\n\n" % ('Logfile',self.logfile))
		new_file.close()
		return True


if __name__ == '__main__':
	r = Rsync('/usr/discreet','destination/',dry_run=False,log_message="Rsync: 10 of 2000: some_directory",delete=True)
	print r.command
	#r.rsync()
