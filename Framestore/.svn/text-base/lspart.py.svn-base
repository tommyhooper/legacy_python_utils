#!/usr/bin/env python
import os
import sys
import commands
import re
import time
import getopt
import pprint
sys.path.append("/Volumes/discreet/dev/python2.3/site-packages")
sys.path.append("/Volumes/discreet/dev/python2.3/site-packages/wiretap")
from A52.utils.xmlparsers import xml_to_dict
from A52.utils import print_array

from libwiretapPythonClientAPI import *

class lspart:

	# some ENUMS and so such 
	NODETYPES= {0: "NODE",
			1: "HOST",
			2: "VOLUME",
			3: "PROJECT",
			4: "LIBRARY",
			5: "REEL",
			6: "CLIP",
			7: "CLIP_HIRES",
			8: "CLIP_LOWRES",
			9: "CLIP_SLATE",
			10: "CLIP_AUDIO",
			11: "CLIP_AUDIO_STREAM",
			12: "USER",
			13: "SETUP",
			14: "USER_PREFERENCE"
			}

	rootpath = "/stonefs4"

	DEPTHS = {	16: 134,
			12: 134,
			10: 136,
			8: 130,
			}

	DEPTHSA ={	16: 128,
			12: 128,
			8: 131,
			}

	SCANFORMAT = {	"SCAN_FORMAT_PROGRESSIVE":  "progressive",
				"SCAN_FORMAT_FIELD_1_ODD":  "field1_odd",
				"SCAN_FORMAT_FIELD_2_ODD":  "field2_odd",
				"SCAN_FORMAT_FIELD_1_EVEN": "field1_even",
				"SCAN_FORMAT_FIELD_2_EVEN": "field2_even",
				"SCAN_FORMAT_UNKNOWN":			"unknown",
				}

	def __init__(self,hostname):
		""" Initiate the connection to the WireTap Server """
		self.hostname = hostname
		if not WireTapClientInit():
			raise "Unable to initialize WireTap client API."
		self.server = WireTapServerHandle( self.hostname )
		if not self.server.ping():
			raise "Unable to connect to WireTap Server"

	# this crashes for some reason
	# def __del__(self):
	#	WireTapClientUninit()

	def get_children(self, parent, type=None):
		""" get a list of children from a node """
		numChildren = WireTapInt( 0 )
		if not parent.getNumChildren( numChildren ):
			return ()
		child = WireTapNodeHandle ()
		i = 0
		children = []
		while i < numChildren:
			parent.getChild( i, child )
			i += 1
			name = WireTapStr()
			typeStr = WireTapStr()
			nodeID = WireTapStr( child.getNodeId().id() )
			if not child.getDisplayName( name ):
				raise 'Unable to obtain node name: %s.' % child.lastError()
			if not child.getNodeTypeStr( typeStr ):
				raise 'Unable to obtain node type: %s.' % child.lastError()
			node =  {	"Name":   name.c_str(),
					"Type":   typeStr.c_str(),
					"NodeId": nodeID.c_str()
					} 
			# are we only looking for a certain type of node ?
			if type:
				if typeStr.c_str() == type:
					children.append( node )
			else:
				children.append( node )
		return children
	
	def get_projects(self):
		""" Returns a list of projects """
		parent = WireTapNodeHandle( self.server, self.rootpath )
		projects = []
		children = self.get_children(parent,type="PROJECT")
		for child in children:
			projects.append( child )
		return projects

	def get_project(self,project):
		""" Returns the list of Libraries for a project """
		parent = WireTapNodeHandle( self.server, self.rootpath + "/%s" %  project )
		libraries = []
		children = self.get_children(parent,type="LIBRARY")
		for child in children:
			libraries.append( child)
		return libraries
  
	def get_library(self,project,library):
		""" Returns the content of a library """
		parent = WireTapNodeHandle( self.server, self.rootpath + "/%s/%s" % ( project , library) )
		nodes = []
		children = self.get_children(parent)
		for child in children:
			if child['Type'] == 'REEL':
				reel = WireTapNodeHandle(self.server, child['NodeId'])
				reel_children = self.get_children( reel )
				for reel_child in reel_children:
					if reel_child['Type'] == 'REEL':
						subreel = WireTapNodeHandle(self.server, reel_child['NodeId'])
						subreel_children = self.get_children( subreel )
						for subreel_child in subreel_children:
							subreel_child['Name'] = child['Name'] + "/" + reel_child['Name'] + "/" + subreel_child['Name']
							nodes.append( subreel_child )
					else:
						reel_child['Name']= child['Name'] + "/" + reel_child['Name']
						nodes.append( reel_child )
			else:
				nodes.append( child )
		return nodes

	def get_clip(self,project,library,clip):
		""" Returns a clip's NodeId """
		children = self.get_library(project,library)
		for child in children:
			if "/%s" % child['Name'] == clip:
				if child['Type'] == 'CLIP':
					return child['NodeId']
		return None

	def clip_info(self, nodeId):
		""" Returns information from a nodeId """ 
		clip = WireTapNodeHandle( self.server, nodeId)
		children = self.get_children(clip)
		Name = WireTapStr()
		numFrames = WireTapInt()
		ImageFormat = WireTapClipFormat()
		typeStr = WireTapStr()
		metadata = WireTapStr()
		if not clip.getNodeTypeStr( typeStr ):
			raise "Unable to retrieve node type: %s\n" % clip.lastError()
		if not clip.getNumFrames( numFrames ):
			raise 'Unable to obtain number of frames: %s.' % clip.lastError()
		if not clip.getClipFormat( ImageFormat ):
			raise 'unable to obtain clip format: %s.' % clip.lasterror()
		if not clip.getDisplayName(Name ):
			raise 'Unable to obtain Display Name: %s.' % clip.lastError()
		scanFormat = ImageFormat.scanFormat()
		if ( cmp( ImageFormat.formatTag(), WireTapClipFormat.FORMAT_DL_AUDIO_INT24() ) ==0 ):
			pass
		if ImageFormat.formatTag() == "rgb" or ImageFormat.formatTag() == "rgb_le":
			depth = self.DEPTHS[int(ImageFormat.bitsPerPixel()) / int(ImageFormat.numChannels())]
		else:
			depth = self.DEPTHSA[int(ImageFormat.bitsPerPixel()) / int(ImageFormat.numChannels())]
		ret = { 
				"NodeId":		nodeId,
				"Type":		typeStr.c_str(),
				"Bytes":		ImageFormat.frameBufferSize(),
				"BitsPerPixel":	ImageFormat.bitsPerPixel(),
				"Channels":		ImageFormat.numChannels(),
				"FrameRate":	ImageFormat.frameRate(),
				"ScanFormat":	ImageFormat.scanFormat(),
				"Width":		ImageFormat.width(), 
				"Height":		ImageFormat.height(),
				"Depth":		depth,
				"FPS":		ImageFormat.frameRate(),
				"Format":		ImageFormat.formatTag(),
				"BufferSize":	ImageFormat.frameBufferSize(),
				"Frames":		int(numFrames),
				"PixelRatio":	ImageFormat.pixelRatio(),
				"Name":		Name.c_str(),
				"Server":		clip.getServer(),
				"Metadata":		xml_to_dict(ImageFormat.metaData()),
				"MetadataStr":	ImageFormat.metaData(),
				"Children":		len(children),
				}
		for child in children:
			if child['Type'] == 'AUDIOSTREAM':
				cclip = WireTapNodeHandle( self.server, child['NodeId'] )
				audioFormat = WireTapAudioFormat()
				if not cclip.getClipFormat( audioFormat ):
					raise 'unable to obtain clip audio format: %s.' % cclip.lasterror()
				audio = {}
				audio['Audio'] = {
							'NumSamples':			audioFormat.numSamples(),
							'BitsPerSample':			audioFormat.bitsPerSample(),
							'NumChannels':			audioFormat.numChannels(),
							'SampleRate':			audioFormat.sampleRate(),
							'FormatTag':			audioFormat.formatTag(),
							'Metadata':				audioFormat.metaData(),
							}
				ret.update(audio)
			if child['Type'] == 'HIRES':
				clip_node = WireTapNodeHandle( self.server, child['NodeId'])
				n = WireTapInt()
				clip.getNumFrames(n)
				x = 0
				while x < n:
					path = WireTapStr()
					clip_node.getFrameIdPath( x, path)
					print "\t>:",path.c_str()
					x += 1
		try:
			xml = xml_to_dict(ImageFormat.metaData())['ClipData']
			if xml: ret.update(xml)
		except:
			pass
		return ret



if __name__ == "__main__":
	import socket

	from optparse import OptionParser
	usage = """usage: lspart [project] [library] [clip]"""
	parser = OptionParser(usage=usage)
	parser.add_option("-H","--hostname", dest="hostname", type="string", help="Hostname to query")
	parser.add_option("-n","--nodeid", dest="nodeid", action="store_true", help="output NodeID")
	parser.add_option("-f","--format", dest="format", action="store_true", help="output Detail format")
	parser.add_option("-a","--audio", dest="audio", action="store_true", help="output Audio Info")
	(options, args) = parser.parse_args()
	if options.hostname is None:
		hostname = socket.gethostname()
	else:
		hostname = options.hostname
	l = lspart(hostname)
	if len(args)==0:
		print "--------------------"
		for p in l.get_projects():
			print p['Name']
	elif len(args)==1:
		print "--------------------"
		print "Free Frames: 1000"
		for p in l.get_project(args[0]):
			print p['Name']
	elif len(args)==2:
		print "--------------------"
		for node in l.get_library(args[0],args[1]):
			print "/%s" % node['Name']
			clip = l.clip_info(node['NodeId'])
			print time.strftime("%y/%m/%d %H:%M:%S", time.strptime(clip['Metadata']['ClipData']['ClipCreationDate']) )
			print "%s - %s" % ( clip['Metadata']['ClipData']['Duration'], clip['Frames'] )
			if options.nodeid:
				print clip["NodeId"]
	elif len(args)==3:
		print "--------------------"
		clip = l.get_clip(args[0],args[1],args[2])
		if not clip: sys.exit(0)
		clip = l.clip_info(clip)
		print "Bytes				: %s" % clip['BufferSize']
		print "Width				: %s" % clip['Width']
		print "Height				: %s" % clip['Height']
		print "Depth				: %s" % clip['Depth']
		print "Frames				: %s" % clip['Frames']
		print "AspectRatio : %04f" % ( float(clip['Width']) / float(clip['Height']) )
		print "FrameRate   : %s" % clip['FrameRate']
		print "hours				: %02d" % int(clip['Metadata']['ClipData']['SrcTimecode'][0:2] )
		print "minutes				: %02d" % int(clip['Metadata']['ClipData']['SrcTimecode'][3:5] )
		print "seconds				: %02d" % int(clip['Metadata']['ClipData']['SrcTimecode'][6:8] )
		print "frames				: %02d" % int(clip['Metadata']['ClipData']['SrcTimecode'][9:11] )
		print "scanformat  : %s" % l.SCANFORMAT["%s" % clip['ScanFormat']]
		if int(clip['BitsPerPixel']) == 48:
			print "unpacked		: 1"
		else:
			print "unpacked		: 0"
		if options.nodeid:
			print "nodeId			: %s" % clip["NodeId"]
		if options.format:
			print "format			: %s" % clip["Format"]
			print "bits			: %s" % ( int(clip["BitsPerPixel"]) / int(clip["Channels"] ) )
			print "children		: %s" % clip['Children']
			print "metadata		: %s" % clip['MetadataStr']
		if options.audio:
			if 'Audio' in clip.keys():
				print "audioBitsperSample : %s" % clip["Audio"]['BitsPerSample']
				print "audioNumChannels   : %s" % clip["Audio"]['NumChannels']
				print "audioNumSamples			: %s" % clip["Audio"]['NumSamples']
				print "audioFormatTag			: %s" % clip["Audio"]['FormatTag']
				print "audioSampleRate			: %s" % clip["Audio"]['SampleRate']
				print "audioMetadata			: %s" % clip["Audio"]['Metadata']


