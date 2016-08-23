from A52.utils import dateutil
from A52.utils import numberutil
from A52.utils import print_array
from datetime import datetime
import time
import os
import sys
import threading
import signal
import re
import bz2
import popen2 # Deprecated ./fuse_2011.py:5: DeprecationWarning: The popen2 module is deprecated.  Use the subprocess module.
import signal
from select import select 

class rsync_thread(object):


	def __init__(self):
		self.running = False
		# integer indicating which queue entry is running
		self.queue = []
		self.current_queue_entry = None
		self.reset_progress()
		self.reset_stats()
		self.current_log = None

	def add(self,source,destination,logfile=None,dry_run=None):
		commands = self.form_commands(source,destination)
		entry = {	'source':source,
				'destination':destination,
				'dry_run':dry_run,
				'commands':commands,
				'logfile':logfile,
				'job_status':'queued'}
		self.queue.append(entry)

	def form_commands(self,source,destination):
		fmt = "--out-format='::%l:%f'"
		dry_run = "rsync -avn --stats %s %s %s" % (fmt,source,destination)
		command = "rsync -av %s %s %s" % (fmt,source,destination)
		return (dry_run,command)
	
	def get_jobs(self):
		return self.queue

	def __del__(self):
		"""
		Cleanup on exit
		"""
		#print "Closing logfile"
		if self.current_log:
			self.current_log.close()

	def start(self):
		#print "Starting rsync thread"
		threading.Thread(target=self._start).start()
		self.running = True

	def stop(self):
		#print "Stopping rsync thread"
		self._stopped = true

	def status(self):
		return self.progress

	def readline_progress(self,line):
		if line[0:2] == '::':
			try:
				self.progress['current_file'] = line.split(':')[3]
				self.progress['elapsed_time'] = int(time.time()) - self.progress['start_time']
				_bytes = int(line.split(':')[2])
				if _bytes > 0 and self.progress['elapsed_time'] > 0:
					self.progress['bytes_transferred']+= _bytes
					self.progress['rate'] = self.progress['bytes_transferred'] / (self.progress['elapsed_time']*1.0)
					if self.stats['rsync_bytes'] > 0:
						percent = int(round((self.progress['bytes_transferred']/ (self.stats['bytes_to_transfer']*1.0))*100,0))
					else:
						percent = 0
					if percent > 100: percent = 100
					self.progress['percent_done'] = percent
				print "Complete: %s%%\t%s/sec   \r" % (self.progress['percent_done'],numberutil.humanize(self.progress['rate'],scale='bytes')),
				sys.stdout.flush()
	
				#(Q:1/10) 35% 400Mb (24/MB/sec) ::/tmp/discreet/kjafkj/jasdkjsl/ajsdkjskdf/jasdkfajsld
				logline = "(Q:%s/%s) %s%% %s (%s/sec) :: %s\n" % (	self.current_queue_entry+1,
													len(self.queue),
													self.progress['percent_done'],
													numberutil.humanize(self.progress['bytes_transferred'],scale='bytes'),
													numberutil.humanize(self.progress['rate'],scale='bytes'),
													self.progress['current_file'])
				self.log.write(logline)
			except:pass


	def readline_stats(self,line):
		if line[0:2] == '::':
			try:
				_bytes = int(line.split(':')[2])
				self.stats['bytes_to_transfer']+= _bytes
			except: pass
		if "Number of files:" in line:
			self.stats['source_file_count'] = int(line.split(':')[1].strip())
			self.log.write("#%24s: %s\n" % ('Total files in source',self.stats['source_file_count']))
		if "Number of files transferred:" in line:
			self.stats['rsync_file_count'] = int(line.split(':')[1].strip())
			self.log.write("#%24s: %s\n" % ('Total files to rsync',self.stats['rsync_file_count']))
		if "Total file size:" in line:
			self.stats['rsync_bytes'] = int(line.split(':')[1].strip().split(' ')[0])
			self.log.write("#%24s: %s\n" % ('Total bytes to transfer',self.stats['rsync_bytes']))

	def _rsync(self,command,line_reader):
		"""
		Start method
		"""
		self._stopped = False
		# spawn the command in a subprocess and wait for it to exit.
		job = popen2.Popen4(command,0)
		while job.poll() == -1:
			sel = select([job.fromchild], [], [], 0.05)
			if job.fromchild in sel[0]:
				output = os.read(job.fromchild.fileno(), 16384),
				for line in output[0].split("\n"):
					line_reader(line)
				if self._stopped:
					os.kill(job.pid,signal.SIGTERM)
					break
			time.sleep(0.01)
		# read till the end of the file
		while output != '':
			output = os.read(job.fromchild.fileno(), 16384)
			for line in output.split("\n"):
				line_reader(line)
		if job.poll():
			print "\n>>> Caught Error: %s\n" % job.poll()
			return False
		else:
			return True

	def reset_stats(self):
		if self.current_queue_entry != None:
			# put the last progress stats into the entry
			self.queue[self.current_queue_entry]['stats'] = dict.copy(self.stats)
		self.stats = {	'bytes_to_transfer':0,
					'source_file_count':0,
					'rsync_file_count':0,
					'rsync_bytes':0
					}

	def reset_progress(self):
		if self.current_queue_entry != None:
			# put the last progress stats into the entry
			self.queue[self.current_queue_entry]['progress'] = dict.copy(self.progress)
		self.progress = {	'current_file':None,
					'bytes_transferred':0,
					'elapsed_time':0,
					'percent_done':0,
					'rate':0,
					'start_time':None,
					}

	def start_log(self):
		log = "/tmp/rsync_log_%s" % (dateutil.legible_date(datetime.today(),19))
		print "Logging to:",log
		#log = self.queue[job_num]['logfile']
		self.log = open(log,'a')

	def log_header(self,job_num):
		header = "# --------------------- RSYNC LOG ---------------------\n"
		header+= "#%24s: %s      \n" % ('Date',dateutil.legible_date(datetime.today(),12))
		header+= "#%24s: %s (of %s)\n" % ('Queue entry',job_num+1,len(self.queue))
		header+= "#%24s: %s\n" % ('Source',self.queue[job_num]['source'])
		header+= "#%24s: %s\n" % ('Destination',self.queue[job_num]['destination'])
		self.log.write(header)

	def stop_log(self):
		stoptime = dateutil.legible_date(datetime.today(),12)
		self.log.write("\n\n# DONE at %s \n" % (stoptime))
		self.log.close()

	def _start(self):
		"""
		Start method
		"""
		self._stopped = False
		if self.current_queue_entry == None:
			job_num = 0
		else:
			job_num = self.current_queue_entry
		self.start_log()
		while job_num < len(self.queue):
			entry = self.queue[job_num]
			self.reset_progress()
			self.current_queue_entry = job_num
			dry_run,normal_run = entry['commands']
			# open the logfile
			self.log_header(job_num)
			# run the stat run
			entry['job_status'] = 'analyzing'
			self.progress['start_time'] = int(time.time())
			success = self._rsync(dry_run,self.readline_stats)
			if success:
				# run the normal run
				if not entry['dry_run']:
					entry['job_status'] = 'running'
					success = self._rsync(normal_run,self.readline_progress)
				entry['job_status'] = 'done'
			else:
				entry['job_status'] = 'error'
			self.running = False
			self.stop_log()
			job_num+=1


class Rsync:
	"""
	Wrapper class for the rsync_thread class.
	Spawns an rsync in a thread then loops updating
	the status every 'x' seconds
	"""
	def __init__(self):
		self.threads = {}
		print "PID:",os.getpid()

	def create_thread(self):
		next_thread_num = len(self.threads)
		self.threads[next_thread_num] = {'thread':rsync_thread()}
		return next_thread_num

	def add_job(self,thread_num,source,destination,logfile='/tmp/rsync_log',dry_run=False,log_message=None):
		if not self.threads.has_key(thread_num):
			print "Error, invalid thread #: %s" % thread_num
			return False
		self.threads[thread_num]['thread'].add(source,destination,logfile=logfile,dry_run=dry_run)
		entry = {	'progress_file':"%s.prog" % (os.path.splitext(logfile)[0]),
				'source':source,
				'destination':destination,
				'logfile':logfile,
				'log_message':log_message,
				'dry_run':dry_run,
				'thread_status':'idle',
				}
		self.threads[thread_num].update(entry)

	def print_queue(self,thread_num=None):
		if thread_num:
			threads = [thread_num]
		else:
			threads = self.threads.keys()
		for num in threads:
			print "\nThread #: %s" % num
			for k,v in self.threads[num].iteritems():
				if k != 'thread':
					print "\t%15s : %s" % (k,v)
			print "\t%15s:" % ('Jobs')
			for job in self.threads[num]['thread'].get_jobs():
				print "\t%15s  %s" % ('',job)

	def start_thread(self,thread_num):
		if self.threads[thread_num]['thread_status'] != 'started':
			print "Thread starting"
			self.threads[thread_num]['thread'].start()
			print "Thread started"
			self.threads[thread_num]['thread_status'] = 'started'
			while self.threads[thread_num]['thread'].running:
#				print "tick"
#				#self.status()
				time.sleep(1)
#			self.thread.stop()

	def stop_thread(self,thread_num):
		if self.threads[thread_num]['thread_status'] == 'started':
			self.threads[thread_num]['thread'].stop()
			self.threads[thread_num]['thread_status'] = 'stopped'
		

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

	def rcv_signal(signum,stack):
		print "Received:",signum,dir(stack)

	signal.signal(signal.SIGUSR1,rcv_signal)
	signal.signal(signal.SIGUSR2,rcv_signal)

if __name__ == '__main__':
	r = Rsync()
	t1 = r.create_thread()
#	r.add_job(t1,'/usr/discreet','destination/',log_message="Entry #1",dry_run=True)
	r.add_job(t1,'/usr/discreet/font/','/Volumes/discreet/font/',log_message="Flame1 discreet fonts",dry_run=True)
#	r.add_job(t1,'/usr/discreet','/tmp/destination2/',log_message="Entry #3",dry_run=False)
#	t2 = r.create_thread()
#	r.add_job(t2,'/usr/discreet','destination/',log_message="Entry #1",dry_run=True)
#	r.add_job(t2,'/usr/discreet','destination/',log_message="Entry #2",dry_run=True)
#	r.add_job(t2,'/usr/discreet','destination/',log_message="Entry #3",dry_run=True)
	r.print_queue()
#	r.start_thread(0)
