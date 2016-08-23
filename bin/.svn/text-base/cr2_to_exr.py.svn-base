#!/usr/bin/python

import sys
import os
import commands
import glob
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import messenger


def help():
	"""
	Print detailed usage on how to use atempo_restore.
	"""
	text = "\nusage: %s <CR2 image file directory>\n" % sys.argv[0]
	print text

def groups(data,length):
	"""
	Iterate through 'data'
	by groups of 'length'
	"""
	for i in xrange(0,len(data),length):
		yield data[i:i+length]

def photomatix(path,outfile,images,num_cores=None):
	"""
	Process 3 'images' through
	a preset PhotmatixCL command line

	# /.kbtmp/PhotomatixCL/PhotomatixCL -3 -h exr -ca -no1 -gh -a2ns -d /mnt/array1/testing/ -n 4 -q 2 _MG_1438.CR2 _MG_1439.CR2 _MG_1440.CR2
	"""
	args = "-3 -h exr -ca -no1 -n 4 -q 1"
	if num_cores > 1:
		args += ' -mp %s' % num_cores
	# form the destination path
	dest_path = "%s/EXR" % (path)
	# form the destination filename
	dest_file = "%s/EXR/%s" % (path,outfile)
	# create the destination path if it's not there
	if not os.path.exists(dest_path):
		os.makedirs(dest_path)
	# form the photomatix command
	command = 'PhotomatixCL %s -d "%s" %s' % (args,dest_file," ".join(images))
	print " ",command
	# run it
	status,output = commands.getstatusoutput(command)
	if status <= 0:
 		print "Error while processing PhotomatixCL: error code [%s]" % status
		print output
		sys.exit()

if __name__ == '__main__':


	# set the default multi-processor value
	mp = 8
	# see if we have a different mp value in the command line
	import getopt
	optlist,args = getopt.getopt(sys.argv[1:],'mp:')
	for opt in optlist:
		if opt[0] == '-p':
			try:
				mp = int(opt[1])
			except:pass

	if len(sys.argv) < 2:
		help()
		sys.exit()

	#for cr2_path in sys.argv[1:]:
	for cr2_path in args:
		start = datetime.today()
		if cr2_path[0] == '/':
			full_path = cr2_path
		else:
			full_path = os.path.abspath(cr2_path)
		print '\nProcessing "%s" ' % full_path

		# collect every file in the directory
		os.chdir(full_path)
		_files = glob.glob("*")

		# filter out only the cr2 files
		cr2_files = []
		for _file in _files:
			if _file[-3:].lower() == 'cr2':
				cr2_files.append(_file)

		# check that the number of cr2 files 
		# we have can be grouped be 3s
		if len(cr2_files) % 3.0:
			print "Number of files is not divisible by 3"
			sys.exit()

		# process in groups of 3s
		cr2_files.sort()
		i = 1
		for group in groups(cr2_files,3):
			outfile = '%04d_' % i
			photomatix(full_path,outfile,group,num_cores=mp)
			i+=1
		stop = datetime.today()
		#print "\n  Elapsed: %s\n" % (stop-start)

		# email completion
		from_addr = 'eng@a52.com'
		to_addrs = 'eng@a52.com,arielle@rockpaperscissors.com'
		subject = 'cr2_to_exr complete'
		message = "\nStarted at:    %s\n" % start
		message+= "Completed at:  %s\n" % stop
		message+= "Elapsed:       %s \n" % (stop-start)
		message+= 'Command: %s\n' % (' '.join(sys.argv))
		print message
		messenger.Email(from_addr,to_addrs,subject,message)




