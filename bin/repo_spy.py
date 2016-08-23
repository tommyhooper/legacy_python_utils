#!/usr/bin/env python

#!/usr/bin/python

import sys
import os
import commands
import glob
import threading
import Queue
import time
import traceback
from datetime import datetime

sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
from A52.utils import fileutil

#import xml.etree.ElementTree as ET
import xml.etree.cElementTree as ET



def changed(xml_file):
	"""
	Determine if the xml setup 
	data contains custom reposition
	data.

	state is apparently an integer
	representation of a byte that is used
	to store different toggle states
	state: 	
			0	Reposition
			1	Racking
			2	Off
			256	flip
			1024	flop
			1280	flip & flop
			1281	flip & flop & racking
			1282	flip & flop & off
	
	type:
			0	quality
			1	fast
			2
			3
			4
			5	custom
	"""
	#print "Checking",xml_file
	tree = ET.parse(xml_file)
	root = tree.getroot()
	grade = root.find('grade')
	pan = grade.find('pan')
	zoom = grade.find('zoom')

	# this is our default reposition
	rule = {	'horizontal' : '0',
			'vertical' : '0',
			'state' : '0',
			'rotation' : '0',
			#'type' : '0',
			'scale' : '1.25',
			'aspect' : '1'
		}

	rep = {	'horizontal' : pan.get('x'),
			'vertical' : pan.get('y'),
			'state' : pan.get('state'),
			'rotation' : pan.get('rot'),
			#'type' : pan.get('type'),
			'scale' : zoom.get('x'),
			'aspect' : zoom.get('y')
		}
	if rule != rep:
		print "Changed: %s" % xml_file
		for x,y in rep.iteritems():
			if rule[x] != y:
				print "\t%12s: %s (default: %s)" % (x,y,rule[x])
#			if x == 'state':
#				print "\t%12s: bin: %s" % (x,bin(int(y)))
	



if __name__ == '__main__':

	if len(sys.argv) < 2:
		print "\n%s search_dir\n" % sys.argv[0]
		sys.exit()


	base = sys.argv[1]
	for root,dirs,files in os.walk(base):
		for _file in files:
			if _file[-3:].lower() == "xml":
				changed("%s/%s" % (root,_file))

#	changed(setup)




