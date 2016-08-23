#!/usr/bin/python

import threading
import os
import commands
import Queue
import time
import sys


def help():
	print "\n usage: %s infile start end\n" % (os.path.split(sys.argv[0])[1])



if __name__ == '__main__':

	if len(sys.argv) < 5:
		help()
		sys.exit()

	infile = sys.argv[1]
	start = int(sys.argv[2])
	end = int(sys.argv[3])


	for i in range(start,end+1,1):
		target = infile % i
		command = 'mogrify -write rgb:- %s' % (target)
		print command










