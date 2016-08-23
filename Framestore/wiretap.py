#!/usr/bin/python
import sys
import socket
import os
import platform
import glob
import time
from datetime import datetime

from A52.utils import print_array
from A52.utils import numberutil
from A52.utils import stringutil
try:
	import xml.etree.cElementTree as ElementTree
except:
	#from elementtree import ElementTree
	import cElementTree as ElementTree


import logging
log = logging.getLogger(__name__)
#log = logging.getLogger('DL_MIRROR')
## Stream handler
#stream_handler = logging.StreamHandler(sys.stdout)
#stream_format = logging.Formatter('%(message)s')
#stream_handler.setFormatter(stream_format)
#log.addHandler(stream_handler)
#stream_handler.setLevel(logging.WARNING)
#log.setLevel(logging.DEBUG)



#print "PYTHON VERSION:",sys.version
try:
	from libwiretapPythonClientAPI import *
	__WT_ENABLED__ = True
except:
	if platform.dist()[0] == 'debian':
		try:
			# try to import the debian wiretap api
			sys.path.append('/Volumes/discreet/lib/wiretap/2012/debian')
			from libwiretapPythonClientAPI import *
			__WT_ENABLED__ = True
		except:
			message = "Cannot import wiretap API (debian)... disabling\n"
			sys.stderr.write(message)
			__WT_ENABLED__ = False
	if platform.dist()[0] == 'redhat':
		try:
			# try to import the debian wiretap api
			sys.path.append('/Volumes/discreet/lib/wiretap/2012.1.1/redhat')
			from libwiretapPythonClientAPI import *
			__WT_ENABLED__ = True
		except:
			message = "Cannot import wiretap API (redhat)... disabling\n"
			sys.stderr.write(message)
			__WT_ENABLED__ = False

class WiretapException(Exception):
	pass

class Wiretap:
	"""
	Wrapper class for libWiretapPythonClientAPI
	"""

	def __init__(self,host):
		"""
		Init the wiretap connection
		"""
		self.host = host

	def __getattr__(self,name):
		"""
		Catch self.server to enable the
		wiretap connection
		"""
		if name == 'server':
			self._connect()
			return self.server
		message = "'%s' has no attribute %s" % (__name__,name)
		raise AttributeError,message

	def __del__(self):
		"""
		Uninit the wiretap connection when 
		the object is removed
		"""
		try:self._disconnect()
		except:pass

	def _connect(self):
		#print "Establishing wiretap connection"
		log.debug('WireTapClientInit()')
		if not WireTapClientInit():
			raise WiretapException,"Unable to initialize WireTap client API."
		self.server = WireTapServerHandle( self.host)
		#if not self.server.ping():
		#	raise WiretapException,"Unable to connect to WireTap Server on %s" % (self.host)

	def _disconnect(self):
		log.debug('WireTapClientUninit()')
		#print "Disconnecting"
		WireTapClientUninit();

	def _get_children(self,node=None,node_type=None):
		"""
		List the children for the given 'node' on the framestore.
		'node' can be either a string or a wiretap node
		If node is left blank then the top level is returned.
		(list of volumes i.e. 'stonefs4')
		"""
		log.debug('_get_children: node=%s, node_type=%s' % (node,node_type))
		if node:
			if type(node) is str:
				parent = WireTapNodeHandle(self.server,"/%s" % node.strip("/"))
			else:
				parent = node
		else:
			parent = WireTapNodeHandle()
			self.server.getRootNode(parent)
		numChildren = WireTapInt(0)
		if not parent.getNumChildren(numChildren):
			message = "Error (get_children) (%s:%s:%s): %s" % (self.host,node,node_type,parent.lastError())
			print message
			#raise 'Unable to obtain number of children: %s.' % parent.lastError()
			raise WiretapException,message
		i = 0
		children = {}
		while i < numChildren:
			child = WireTapNodeHandle()
			parent.getChild(i,child)
			name = self._get_node_name(child)
			typeStr = self._get_node_type(child)
			nodeID = WireTapStr( child.getNodeId().id() )
			if node_type:
				if typeStr == node_type:
					children[i] = {	'name':name,
								'type':typeStr,
								'node':child,
								'nodeID':nodeID.c_str()
								}
			else:
				children[i] = {	'name':name,
							'type':typeStr,
							'node':child,
							'nodeID':nodeID.c_str()
							}
			i = i + 1
		return children

	def _get_node_name(self,node):
		name = WireTapStr()
		if not node.getDisplayName(name): 
			raise WiretapException,"Error (_get_node_name):",node.lastError()
		return name.c_str()

	def _get_node_type(self,node):
		typeStr = WireTapStr()
		if not node.getNodeTypeStr(typeStr): 
			error = "Error (_get_node_type):",node.lastError()
			return None
			#raise WiretapException,error
		return typeStr.c_str()

	def _get_node(self,node_name):
		"""
		Get the node represented by 'node_name'
		"""
		node = WireTapNodeHandle(self.server,"/%s" % node_name.strip("/"))
		typestr = WireTapStr()
		if not node.getNodeTypeStr(typestr):
			message = node.lastError()
			print message
			raise WiretapException,message
		return node

	def _get_frame_count(self,node):
		"""
		Get the number of frames from a clip node
		"""
		numFrames = WireTapInt()
		if not node.getNumFrames( numFrames ):
			message = 'Unable to obtain number of frames: %s.' % node.lastError()
			print message
			raise WiretapException,message
		return numFrames
	
	def _get_frame_path(self,node,frame):
		"""
		Get the path of the frame number 'frame' 
		in a clip node
		"""
		path = WireTapStr()
		node.getFrameIdPath( frame, path)
		return path.c_str()

	def _get_metadata(self,node):
		"""
		Get the metadata of a node
		"""
		node = WireTapNodeHandle(self.server,"/%s" % node.strip("/"))
		xml = WireTapStr()
		if not node.getMetaData("XML","",1,xml):
			raise WiretapException,'Unable to obtain node metadata: %s.' % node.lastError()
		node.getMetaData("XML","",1,xml)
		return xml.c_str()

	def _create_node(self,parent,node_type,node_name,xmlstream=None):
		"""
		Create a wiretap node under the parent.
		e.g.
		Create a project:
			create_node('flame1','/stonefs4','PROJECT','verizon')
		Create a library:
			create_node('flame1','/stonefs4/verizon','LIBRARY','in')
		Create a user:
			create_node('flame1','/stonefs4/users/effects','USER','tommy')
		"""
		parent_node = WireTapNodeHandle(self.server,'/%s' % (parent.strip('/')))
		new_node = WireTapNodeHandle()
		if type(node_name) is not list:
			node_name = [node_name]
		for name in node_name:
			if not parent_node.createNode(name,node_type,new_node):
				error = parent_node.lastError()
				message = "Error creating wiretap node: %s" % error
				raise WiretapException,message
			if xmlstream:
				if not new_node.setMetaData("XML",xmlstream):
					error = new_node.lastError()
					message = "Error setting xmlstream: %s" % error
					raise WiretapException,message
		return True

	#@staticmethod
	def list_all():
		"""
		Return a list of available framestores
		"""
		# Initialize the Wiretap Client API.
		if not WireTapClientInit():
			raise WiretapException,"Unable to initialize WireTap client API."
		# Obtain the list of Wiretap servers.
		srv_list = WireTapServerList()
		count = WireTapInt()
		if not srv_list.getNumNodes( count ):
			raise WiretapException,"Error acquiring server list: %s." %srv_list.lastError()

		print "Server                IP address  Storage Id     Protocol"
		print "---------------------------------------------------------"
		# Obtain information about each server.
		i = 0
		while i < count:
			info = WireTapServerInfo()
			if not srv_list.getNode( i, info):
				raise WiretapException,"Error accessing server %d: %s." %( i, srv_list.lastError() )
			if info.getVersionMinor() == 0:
				print "%-16s %15s  %-16s %d.%d" % ( info.getDisplayName(), 
									info.getHostname(), 
									info.getStorageId(),
									info.getVersionMajor(), 
									info.getVersionMinor() )
			i = i + 1
		# Uninitialize WireTap services.
		WireTapClientUninit()
	# static and class method definitions
	list_all = staticmethod(list_all)

	def get_frames(self,clip,stream='XML'):
		"""
		Get all the frames out of a clip node
		including soft edits
		"""
		log.debug('get_frames: clip=%s' % clip)
		if stream == 'XML':
			return self._get_frames_xml(clip)
		elif stream == 'DMXEDL':
			return self._get_frames_dmxedl(clip)
		elif stream == 'BOTH':
			xml = self._get_frames_xml(clip)
			dmx = self._get_frames_dmxedl(clip)
			print "XML | DMX: %10s | %-10s" % (len(xml),len(dmx))
			return xml

	def _get_frames_xml(self,clip):
		"""
		Get the frames contained within a clip
		using the XML metadata stream
		"""
		metaData = WireTapStr()
		if not clip.getMetaData("XML","video_only",256,metaData):
			if clip.lastError() != "The given clip ID does not have any video media":
				message = 'Unable to retrieve meta data for %s: %s\n' % (self._get_node_name(clip),clip.lastError())
				raise WiretapException,message
			else:
				log.debug("get_frames: returning []:",clip.lastError())
				return []
		xml_stream = metaData.c_str()
		tree = ElementTree.XML(xml_stream)
		frames = {}
		for element in tree.getiterator():
			if element.tag == 'Frame':
				if element.attrib.has_key('path'):
					frames[element.attrib['path']] = True
		return frames

	def _get_frames_dmxedl(self,clip):
		"""
		Get the frames contained within a clip
		using the dreaded DMXEDL metadata stream
		(aka the wiretapd killer)
		"""
		metaData = WireTapStr()
		if not clip.getMetaData("DMXEDL","",256,metaData):
			if clip.lastError() != "The given clip ID does not have any video media":
				message = 'Unable to retrieve meta data for %s: %s\n' % (self._get_node_name(clip),clip.lastError())
				raise WiretapException,message
			else:
				log.debug("get_frames: returning []:",clip.lastError())
				return []
		metaDataList = metaData.c_str().split("\n")
		frames = {}
		for l in metaDataList:
			split = l.split(":")
			if len(split) > 2 and 'EDIT' in split[1] and 'FRAME' in split[2]:
				framebit = split[3].split()
				if len(framebit) == 2:
					frames[framebit[1]] = True
		return frames

	def test(self):
		#children = self._get_children('/stonefs4/11A163-Nescafe_Hypnotist_MASTER/CONFORMS/H_-1463759519_S_1309291224_U_12926')
		#nodeID = '/stonefs4/11A163-Nescafe_Hypnotist_MASTER/CONFORMS/H_-1463759519_S_1309291224_U_12926/H_-1463759519_S_1309291224_U_27636'
		#{'node': <libwiretapPythonClientAPI.WireTapNodeHandle object at 0x2b36a74ea680>, 'type': 'CLIP', 'name': 'IBM_DC_CONFORM_B', 'nodeID': '/stonefs4/11A173-IBM_Errol_Vers_MASTER/SMOKE_DESKTOP/H_-1463760799_S_1317074999_U_442008/H_-1463760799_S_1317074999_U_442012'}

		#nodeID = '/stonefs4/11A173-IBM_Errol_Vers_MASTER/VFX/H_-1463760543_S_1316020344_U_953315/H_-1463760543_S_1316020348_U_522659'
		nodeID = '/stonefs4/11A173-IBM_Errol_Vers_MASTER/SMOKE_DESKTOP/H_-1463760799_S_1317074999_U_442008/H_-1463760799_S_1317074999_U_442012'
		clip = self._get_node(nodeID)
		name = WireTapStr()
		clip.getDisplayName(name)
		print "CLIP NAME:",name.c_str()

		metaData = WireTapStr()
		if not clip.getMetaData("DMXEDL","",256,metaData):
			if clip.lastError() != "The given clip ID does not have any video media":
				raise WiretapException('Unable to retrieve meta data: %s\n' % clip.lastError())
			else:
				return

		return 
		metaDataList = metaData.c_str().split("\n")
		frames = {}
		for l in metaDataList:
			split = l.split(":")
			if len(split) > 2 and 'FRAME' in split[2]:
				framebit = split[3].split()
				if len(framebit) == 2:
					frames[framebit[1]] = True
		# collect the sizes for each frame using 
		# the frame as a key to weed out duplicates
		for frame in frames:
			if frame:
				_stat = os.lstat(frame)
				st_size = _stat.st_size
				if type(st_size) is int:
					frames[frame] = st_size
				else:
					print "ERROR: could not get size for %s" % frame
		# now add up the frame sizes
		total = sum(frames.values())
		print "CLIP SIZE: (%sx) %s" % (len(frames.values()),numberutil.humanize(total,scale='bytes'))
		return total


class Burn(Wiretap):


	def __init__(self,host=None):
		self.host=host
		self.jobs = []

	def burn_servers(self):
		server = WireTapServerHandle('backburner')
		parent = WireTapNodeHandle(server,"/servergroups")
		num = WireTapInt(0)
		parent.getNumChildren(num)
		i = 0
		while i < num:
			node = WireTapNodeHandle()
			parent.getChild(i,node)
			_id = WireTapStr(node.getNodeId().id())
			i+=1

	def burn_jobs(self,job_name=None):
		jobs = self._get_children('/jobs')
		for i,child in jobs.iteritems():
			name = child['name']
			node = child['node']
			obj = BurnJob(name,node)
			self.jobs.append(obj)
			batch_setup = obj.attr['description'].strip(':').strip()
			if not job_name or job_name == obj.attr['state']:
				print "\x1b[m%-36s [33m%-36s[m%12s" % (obj.attr['name'],batch_setup,obj.attr['state'])
			if obj.attr['name'] == job_name or batch_setup == job_name:
				obj.status()
				return obj
	def job_status(self,job_name):
		job = filter(lambda obj:obj.attr['name'] == job_name, self.jobs)[0]
		job.status()

class BurnServer:


	def __init__(self,name):
		self.name = name
		self.tasks = []

	def first_task(self):
		"""
		Find and return the first task in the list of tasks
		"""
		#for task in self.tasks:
		#	print "    >> %s" % task.attr['startTime']
		return sorted(self.tasks, key=lambda x: stringutil.extract_numbers(x.attr['startTime']))[0]

	def node_log(self):
		"""
		Find the log that goes with the current task list
		"""
		first_task = self.first_task()
		if not first_task:
			return
		print "\nNODE:",self.name
		print "   start time:",first_task.attr['startTime']
		date = first_task.attr['startTime']
		task_start = time.mktime(time.strptime(date.split('.')[0], "%Y-%m-%d %H:%M:%S"))

		logdir = "/hosts/%s/usr/discreet/log" % self.name
		shell_logs = glob.glob("%s/burn*shell*log*" % logdir)
		app_logs = glob.glob("%s/burn*app*log*" % logdir)

		deltas = []
		for sl in shell_logs:
			_stat = os.lstat(sl)
			diff = _stat.st_mtime - task_start
			if diff > 0:
				deltas.append((diff,sl))

		for d in sorted(deltas):
			print "  %s: %s" % (d)
		target = min(deltas)
		return target[1]


class BurnJob:


	def __init__(self,name,node):
		self.name = name
		self.node = node
		self.attr = {}
		self.tasks = []
		self.servers = []
		self._get_info()
		
	def status(self):
		self._get_details()
		self._get_tasks()
		print "[44mJob:[m [%s:%sx] %s" % (self.attr['ClientComputer'],len(self.tasks),self.attr['BatchSetup'])
		print "  Burn name:",self.attr['name']
		print "  Current state:",self._get_state()
		for task in self.tasks:
			print "   [33mTask:[m %(number)-8s%(state)-12s%(server)-10s%(elapsedTime)-16s%(startTime)-12s" % (task.attr)
			if task.attr['lastError']:
				for line in task.attr['lastError'].split('\n'):
					if line != '':
						print "    \x1b[38;5;241m%s\x1b[m" % (line)

	def list_logs(self):
		self._get_servers()
		self._get_node_logs()
		for server in self.servers:
			log = server.node_log()
			print "%s: %s" % (server.name,log)

	def _get_servers(self):
		server_names = []
		for task in self.tasks:
			server = next((x for x in self.servers if x.name == task.attr['server']),None)
			if not server:
				server = BurnServer(task.attr['server'])
				self.servers.append(server)
			server.tasks.append(task)

	def _get_state(self):
		state = WireTapStr()
		self.node.getMetaData("state","",1,state)
		return state.c_str()

	def _get_details(self):
		#node.getMetaData("details","",1,xml) 	# empty
		xml_str = WireTapStr()
		self.node.getMetaData("xmlDetails","",1,xml_str)
		xml_stream = xml_str.c_str()
		tree = ElementTree.XML(xml_stream)
		for element in tree.getiterator():
			self.attr[element.tag] = element.text

	def _get_info(self):
		info_str = WireTapStr()
		self.node.getMetaData("info","",1,info_str)
		xml_stream = info_str.c_str()
		tree = ElementTree.XML(xml_stream)
		for element in tree.getiterator():
			self.attr[element.tag] = element.text

	def _get_tasks(self):
		tasks_str = WireTapStr()
		self.node.getMetaData("tasks","",1,tasks_str)
		xml_stream = tasks_str.c_str()
		tree = ElementTree.fromstring(xml_stream)
		for task in tree.findall('task'):
			obj = BurnTask(task)
			self.tasks.append(obj)
	
	def _get_node_logs(self):
		"""
		Figure out the first task for each node
		then try to find the logfile with 
		the nearest date.
		"""
		pass


class BurnTask:


	def __init__(self,xml_element):
		self.element = xml_element
		self.attr = {}
		self._set_attributes()
		#self._find_logfiles()

	def _set_attributes(self):
		for attr in self.element:
			self.attr[attr.tag] = attr.text
	
	def _find_logfiles(self):
		# note: store the inode once we find it
		# + startTime => 2013-03-15 13:09:59.858
		# + server => burn06

		node = self.attr['server']
		task_start = time.mktime(time.strptime(self.attr['startTime'].split('.')[0], "%Y-%m-%d %H:%M:%S"))

		logdir = "/hosts/%s/usr/discreet/log" % node
		shell_logs = glob.glob("%s/burn*shell*log*" % logdir)
		app_logs = glob.glob("%s/burn*app*log*" % logdir)

		deltas = []
		for sl in shell_logs:
			_stat = os.lstat(sl)
			diff = _stat.st_mtime - task_start
			if diff > 0:
				deltas.append((diff,sl))

		target = min(deltas)
		print "TARGET LOG:",target



		

if __name__ == '__main__':
#	Wiretap.list_all()
	w = Burn(host='backburner')
	if len(sys.argv) > 1:
		w.burn_jobs(sys.argv[1])
	else:
		w.burn_jobs()
#		job = sys.argv[1]
#		w.job_status(sys.argv[1])

#	xml = w._get_metadata('flame4','stonefs4/11A107-Nintendo_3DS_Glynt')
#	print "XML:",xml
#	children = w._get_children('flame3')
#	for i in children:
#		print "CHILD:",children[i]
	pass

#CLIP: {'node': <libwiretapPythonClientAPI.WireTapNodeHandle object at 0x2b59d1c0df70>, 'type': 'CLIP', 'name': 'TCHR1700.MOV', 'nodeID': '/stonefs4/11A173-IBM_Errol_Vers_MASTER/VFX/H_-1463760543_S_1316020344_U_953315/H_-1463760543_S_1316020348_U_522659'}

