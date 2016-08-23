#!/usr/bin/python

import os
import sys
path = os.path.dirname(os.path.abspath(__file__))
if "/dev/" in path:
	print "Loading dev path"
	sys.path.append('/Volumes/discreet/dev/python2.3/site-packages')
else:
	sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')

from A52.utils import swutil

swutil.sw_wiretapd()
