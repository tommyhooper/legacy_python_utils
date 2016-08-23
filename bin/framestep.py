#!/usr/bin/python

import glob
import shutil
import os

from optparse import OptionParser
p = OptionParser()
p.add_option("-s",dest='step',help="Step number")
options,args = p.parse_args()

if len(args) == 0:
	print "\nusage: %s -s <step> path\n" % sys.argv[0]
	sys.exit()

if not options.step:
	print "Must specificy a step value"
	sys.exit()

# make sure our step value is an integer
step = int(options.step)

# multiple paths can be fed to the command
for path in args:
	print "Renumbering",path
	# get all the files out of the path
	files = glob.glob("%s/*" % path)
	# we're relying on the list
	# to be in numerical order
	# NOTE: this is not a true numerical
	# sort and will probably fail on %01d padding
	files.sort()

	# split up the filename
	split = files[0].split('.')
	name = '.'.join(split[:-2])
	framenum = split[-2]
	pad = "%%0%dd" % len(framenum)
	ext = split[-1]

	# iterate through only the files
	# specified by our step value
	for i in range (0,len(files),step):
		source = files[i]
		# copy the source file 'x' times
		# (x is our step value)
		for x in range (1,step,1):
			dest = '%s.%s.%s' % (name,pad % (i+x+1),ext)
			print "%s -> %s" % (os.path.basename(source),os.path.basename(dest))
			#shutil.filecopy(source,dest)

