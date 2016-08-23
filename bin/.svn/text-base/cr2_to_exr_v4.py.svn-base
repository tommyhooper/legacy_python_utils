#!/usr/bin/python

import sys
import os
import commands
import glob
import threading
import Queue
import time
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import messenger

import logging
# create a log for the this module
log = logging.getLogger('PhotomatixCL')
log_handler = logging.handlers.RotatingFileHandler('/var/log/a52_PhotomatixCL.log','a', 20000000, 100)
log_format = logging.Formatter('[%(asctime)s]:%(levelname)7s:%(lineno)5s:%(module)s: %(message)s','%b %d %H:%M:%S')
log_handler.setFormatter(log_format)
log.addHandler(log_handler)

def help():
	"""
	Print detailed usage on how to use atempo_restore.
	"""
	text = """\nusage: %s <CR2 image file directory or directories> [-pt <threads>] [-sf start_frame] [PhotomatixCL arguments]\n
	Custom (non-PhotomatixCL) options:
		-pt <number of threads>		- number of python threads (default is 3)
		-sf <start_frame>	 		- frame to start at (default is 1)

	Optional arguments after image directories will be passed straight through to 
	the PhotomatixCL command. However the following arguments are immutable and will 
	be ignored:
		-3 
		-h exr 
		-n 4
		-q 1 
		-d <images>

	The following arguments are used by default but will NOT be used
	if optional arguments are passed in the command line.
	** SO to turn all options off pass the -mp argument and the rest will be ignored:
		-ca 
		-no1 
		-gh 
		-a3ns 
		-mp 8


		""" % os.path.split(sys.argv[0])[1]
	print text

def groups(data,length):
	"""
	Iterate through 'data'
	by groups of 'length'
	"""
	for i in xrange(0,len(data),length):
		yield data[i:i+length]

def find_cr2_images(path):
	"""
	Walk the 'path' and find CR2 files.
	Return a dictionary in this form:
		{'path to cr2 sequence': [list of cr2 files]}
	"""
	images = {}
	for root,dirs,files in os.walk(path):
		for _file in files:
			if _file[-3:].lower() == "cr2":
				try:
					images[root].append(_file)
				except:
					images[root] = [_file]
	return images

def form_destination_path(source_path,tail_directories=2):
	"""
	Form the destination path based on the given
	'source_path' using the last 'x' number
	of directories at the END of the path.
	The default is to use the last 2 directories
	in the path but this can be changed by 
	using the 'tail_directories' argument.
	"""
	split = source_path.split('/')
	raw_index = split.index('raw')
	dest_head = "%s/exr" % ("/".join(split[0:raw_index]))
	dest_tail = "/".join(split[-tail_directories:])
	return "%s/%s" % (dest_head,dest_tail)

class minion(threading.Thread):
	"""
	Processing thread for the PhotoMatix commands
	"""

	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			obj = self.queue.get()
			if obj is None:
				break
			log.info("%s: %s" % (self.getName(),obj.source_images))
			#print obj.command
			obj.run()
			# python 2.5+
			#self.queue.task_done()

class Photomatix:
	"""
	Photomatix wrapper class.
	Currently this class represents 
	one PhotomatixCL command. It does not
	process sequences. That is handled 
	outside of this class.
	"""

	def __init__(self,source_images,outfile,pass_through_args=None):
		self.source_images = source_images
		self.outfile = outfile
		# static args cannot be overridden
		self.static_args = "-3 -h exr -n 4 -q 1"
		# default args are ignored if user passes their own
		self.default_args = "-ca -no1 -gh -a3ns -mp 8"
		# user args:
		self.pass_through_args = pass_through_args
		# setup the args and the command
		self.parse_args()
		self.form_command()

	def run(self):
		"""
		Run the photomatix command
		and then rename the output
		to the intended output file.
		"""
		if self.check_dest_file():
			return

		self.create_dest_dir()
		if not self.process():
			return
		self.rename_output()

	def parse_args(self):
		"""
		Search through the pass through args for our
		default args.
		"""
		if not self.pass_through_args:
			self.args = "%s %s" % (self.static_args,self.default_args)
			return

		# separate the args into pairs
		static_pairs = self.create_arg_pairs(self.static_args) 

		# if we have user supplied args process 
		# them instead of the default args
		if self.pass_through_args:
			main_pairs = self.create_arg_pairs(self.pass_through_args)
			# make sure the user didn't try to use the -d arg
			if main_pairs.has_key('-d'):
				print "User args: Removing -d option"
				del(main_pairs['-d'])
	
			# the static args take priority over the user args
			# add the user args to the static args that do not conflict
			for k,v in main_pairs.iteritems():
				if static_pairs.has_key(k):
					if v:
						print "User args: Ignoring:",k,v
					else:
						print "User args: Ignoring:",k
			main_pairs.update(static_pairs)
		else:
			# add the default args into the main args 
			main_pairs = self.create_arg_pairs(self.default_args) 
			main_pairs.update(user_pairs)

		self.args = ''
		for k,v in main_pairs.iteritems():
			if v:
				self.args+= " %s %s" % (k,v)
			else:
				self.args+= " %s" % k

	def create_arg_pairs(self,args):
		"""
		Separate args into pairs
		"""
		# args must be a list
		if type(args) is not list:
			args = args.split()
		pairs = {}
		i = 0
		while i < len(args):
			arg = args[i]
			# for the last arg there is no subarg
			if i == len(args):
				pairs[arg] = None 
				break
			subarg = args[i+1]
			if subarg[0] != '-':
				pairs[arg] = subarg
				i+=1
			else:
				pairs[arg] = None
			i+=1
		return pairs

	def process(self):
		"""
		Process the photomatix command
		"""
		# if there is a previous instance of this file
		# we need to remove it since the photomatix
		# command will not overwrite it
		if os.path.exists(self.rendered_file):
			os.remove(self.rendered_file)
		# run it
		log.info("Starting: %s" % self.command)
		self.status,self.output = commands.getstatusoutput(self.command)
		if not os.path.exists(self.rendered_file):
 			msg = "Error while processing PhotomatixCL: error code [%s]" % self.status
			log.error(msg)
			log.error(self.output)
			print msg
			print self.output
			return False
		log.info(self.output)
		return True

	def rename_output(self):
		"""
		Rename the rendered file to 
		the intended destination file.
		"""
		log.info("Renaming: %s -> %s" % (self.rendered_file,self.outfile))
		if os.path.exists(self.rendered_file):
			os.rename(self.rendered_file,self.outfile)
		else:
			msg = "ERROR: Cannot rename rendered file. File is missing: %s" % self.outfile
			log.error(msg)
			print "\nERROR: Cannot rename rendered file. File is missing:"
			print "FILE: %s" % self.outfile

	def check_dest_file(self):
		"""
		Check if the destination file exists.
		"""
		if os.path.exists(self.outfile):
			msg = "File exists: %s" % self.outfile
			log.info(msg)
			print msg
			return True
		return False

	def create_dest_dir(self):
		"""
		create the destination path if it's not there
		"""
		self.dest_path = os.path.split(self.outfile)[0]
		if not os.path.exists(self.dest_path):
			log.info("Creating: %s" % self.dest_path)
			try:
				os.makedirs(self.dest_path)
			except:pass

	def form_command(self):
		"""
		Form the PhotomatixCL command to process 3 CR2 'source_images'
		into an exr. 
	
		# /.kbtmp/PhotomatixCL/PhotomatixCL -3 -h exr -ca -no1 -gh -a2ns -d /mnt/array1/testing/ -n 4 -q 2 _MG_1438.CR2 _MG_1439.CR2 _MG_1440.CR2
		"""
		# form the tmp destination filename
		# photomatix likes to create it's own outfile
		# and will append 'Set01' to this
		dest_file = "%s_" % (os.path.splitext(self.outfile)[0])
	
		# form the photomatix command
		self.command = 'PhotomatixCL %s -d "%s" %s' % (self.args,dest_file,' '.join(self.source_images))

		# we need to return the filename that the photomatix
		# command is going to render since we have no control
		# over how it's finally named.
		self.rendered_file = "%sSet01%s" % (dest_file,os.path.splitext(self.outfile)[1])


if __name__ == '__main__':

	if len(sys.argv) < 2:
		help()
		sys.exit()

	# grab the first non '-' arguments as a directories
	# then treat the remaining arguments as
	# PhotomatixCL args and pass them straight through
	paths = []
	pm_args = None
	for i in range(1,len(sys.argv),1):
		arg = sys.argv[i]
		if arg[0] == '-':
			pm_args = sys.argv[i:]
			break
		else:
			paths.append(arg)

	# check for our specific python thread argument  
	pthreads = 3		# default python thread number
	start_frame = 1 		# start_frame (optional)
	if type(pm_args) is list:
		if '-pt' in pm_args:
			pthreads = pm_args[pm_args.index('-pt')+1]
			if pthreads[0] == '-' or not pthreads.isdigit() :
				print "ERROR: Missing or invalid python thread number (-pt option)"
				sys.exit()
			pthreads = int(pthreads)
			pm_args.pop(pm_args.index('-pt')+1)
			pm_args.pop(pm_args.index('-pt'))
		if '-sf' in pm_args:
			start_frame = pm_args[pm_args.index('-sf')+1]
			if start_frame[0] == '-' or not start_frame.isdigit() :
				print "ERROR: Missing or invalid start frame number (-sf option)"
				sys.exit()
			start_frame = int(start_frame)
			pm_args.pop(pm_args.index('-sf')+1)
			pm_args.pop(pm_args.index('-sf'))

	start = datetime.today()
	# build the queue for the processing threads
	checklist = {}
	queue = Queue.Queue()
	for path in paths:
		# convert the path to absolute
		abs_path = os.path.abspath(path)

		# search for cr2 files
		print "Scanning path for CR2 files: %s" % path
		search = find_cr2_images(abs_path)

		# iterate through the found images
		for source_path in sorted(search):
			images = search[source_path]
			# add this path and the number of images
			# to the checklist
			checklist[source_path] = len(images)

			# form the destination path from the source_path
			dest_path = form_destination_path(source_path)

			# check that the number of cr2 files 
			# we have can be grouped be 3s
			if len(images) % 3.0:
				print "\nERROR: Number of files is not divisible by 3."
				print "PATH: %s\n" % source_path
				sys.exit()

			# process in groups of 3s
			images.sort()
			i = 1
			for group in groups(images,3):
				if i < start_frame:
					print "Skipping frame %04d.exr (start frame set to %s)" % (i,start_frame)
					i+=1
					continue
				outfile = '%s/%04d.exr' % (dest_path,i)
				# add the absolute path to the source images
				source_images = []
				for img in group:
					source_images.append('"%s/%s"' % (source_path,img))
				obj = Photomatix(source_images,outfile,pass_through_args=pm_args)
				queue.put(obj)
				i+=1

	# for older python, put None at the end of the queue
	queue.put(None)

	# spawn worker threads
	for x in range(pthreads):
		thread = minion(queue)
		thread.setDaemon(True)
		thread.start()

	ttl = queue.qsize()
	while not queue.empty():
		crnt = ttl - queue.qsize()
		pct = int(round(crnt/float(ttl)*100))
		print "  Progress: %d of %d [%d%%]\r" % (crnt,ttl,pct),
		sys.stdout.flush()

		# we know the total queue size and 
		# we know the order it's processing in
		# so we should be able to figure out 
		# which shots are done just by subtraction

		time.sleep(1)

	# one last update to catch the 100%
	time.sleep(1)
	crnt = ttl - queue.qsize()
	try:
		pct = int(round(crnt/float(ttl)*100))
	except:
		pct = 100
	print "  Progress: %d of %d [%d%%]" % (crnt,ttl,pct),
	sys.stdout.flush()

	stop = datetime.today()
	# email completion
	from_addr = 'eng@a52.com'
	to_addrs = 'eng@a52.com'
	subject = 'cr2_to_exr complete'
	message = "\nStarted at:    %s\n" % start
	message+= "Completed at:  %s\n" % stop
	message+= "Elapsed:       %s \n" % (stop-start)
	message+= 'Command: %s\n' % (' '.join(sys.argv))
	print message
	messenger.Email(from_addr,to_addrs,subject,message)

	sys.exit()



