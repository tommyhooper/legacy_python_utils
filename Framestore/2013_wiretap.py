#!/usr/bin/python2.4
#!/usr/bin/python
import sys
import socket
import os
import platform
import glob
import time
import shutil
import commands
from datetime import datetime

import logging
log = logging.getLogger(__name__)

from A52.utils import print_array
from A52.utils import numberutil
from A52.utils import fileutil
try:
	import xml.etree.cElementTree as ElementTree
except:
	#from elementtree import ElementTree
	import cElementTree as ElementTree


#print "PYTHON VERSION:",sys.version
sys.path.append('/usr/discreet/flamepremium_2013.2.53.case00540316/python')
#sys.path.append('/Volumes/discreet/dev/wiretap/debian/gcc4_4_6')
#sys.path.append('/Volumes/discreet/dev/wiretap/gcc4_1_2')
#sys.path.append('/Volumes/discreet/dev/wiretap/gcc4_4_6')
#if platform.dist()[0] == 'debian':
#	sys.path.append('/Volumes/discreet/dev/wiretap/debian/gcc4_4_6')
#else:
#	sys.path.append('/usr/discreet/flamepremium_2013.2.2/python')
#	sys.path.append('/usr/discreet/flare_2013.2.2/python')

from libwiretapPythonClientAPI import *
import libwiretapPythonClientAPI as wt
print(sys.version)
print "FILE:",wt.__file__
__WT_ENABLED__ = True



# NOTE: probably will need this on each machine
#       use /usr/bin/uuidgen for the UUID (turn it into caps)
# cat /usr/discreet/cfg/network.cfg 
#[Local]
#UUID=703C1F10-60DD-4B22-885C-812619A59EB7
#DisplayName=tyto
#
#[Interfaces]
#Metadata=vlan10
#Data=vlan10
#Multicast=vlan10
#
#[SelfDiscovery]




class WireTapException(Exception):
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

	def _get_children(self,node=None,node_type=None):
		"""
		List the children for the given 'node' on the framestore.
		'node' can be either a string or a wiretap node
		If node is left blank then the top level is returned.
		(list of volumes i.e. 'stonefs4')

		python -c "from libwiretapPythonClientAPI import *; WireTapClientInit(); server = WireTapServerHandle( 'flame07' ); num = WireTapInt( 0 ); parent = WireTapNodeHandle( server, str('/')); print parent.getNumChildren( num )"
		python -c "from libwiretapPythonClientAPI import *; WireTapClientInit(); server = WireTapServerHandle( 'flame01' ); num = WireTapInt( 0 ); parent = WireTapNodeHandle( server, str('/')); print parent.getNumChildren( num )"


		"""
		WireTapClientInit(); 
		server = WireTapServerHandle(self.host)
		log.debug('_get_children: node=%s, node_type=%s' % (node,node_type))
		if node:
			if type(node) is str:
				parent = WireTapNodeHandle(server,"/%s" % node.strip("/"))
			else:
				parent = node
		else:
			parent = WireTapNodeHandle()
		numChildren = WireTapInt(0)
		if not parent.getNumChildren(numChildren):
			message = "Error (get_children) (%s:%s:%s): %s" % (self.host,node,node_type,parent.lastError())
			print message
			#raise 'Unable to obtain number of children: %s.' % parent.lastError()
			raise WireTapException,message
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
#		WireTapClientUninit();
		return children

	def _get_node_name(self,node):
		name = WireTapStr()
		if not node.getDisplayName(name): 
			raise WireTapException,"Error (_get_node_name):",node.lastError()
		return name.c_str()

	def _get_node_type(self,node):
		typeStr = WireTapStr()
		if not node.getNodeTypeStr(typeStr): 
			error = "Error (_get_node_type):",node.lastError()
			return None
			#raise WireTapException,error
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
			raise WireTapException,message
		return node

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
		WireTapClientInit(); 
		server = WireTapServerHandle(self.host)
		parent_node = WireTapNodeHandle(server,'/%s' % (parent.strip('/')))
		new_node = WireTapNodeHandle()
		if type(node_name) is not list:
			node_name = [node_name]
		for name in node_name:
			if not parent_node.createNode(name,node_type,new_node):
				error = parent_node.lastError()
				message = "Error creating wiretap node: %s" % error
				raise WireTapException,message
			if xmlstream:
				if not new_node.setMetaData("XML",xmlstream):
					error = new_node.lastError()
					message = "Error setting xmlstream: %s" % error
					raise WireTapException,message
		return True

	def _get_metadata(self,node):
		"""
		Get the metadata of a node
		"""
		node = WireTapNodeHandle(self.server,"/%s" % node.strip("/"))
		xml = WireTapStr()
#		if not node.getMetaData("XML","",1,xml):
#			raise WireTapException,'Unable to obtain node metadata: %s.' % node.lastError()
		node.getMetaData("XML","",1,xml)
		return xml.c_str()

	def create_workspace(self,partition,project,workspace):
		"""
		/stonefs6/2013x2_project/workspace
		<Workspace><Name>workspace</Name><WriteCompatible>True</WriteCompatible><Locked>False</Locked></Workspace>

		  NAME: workspace
		  TYPE: WORKSPACE
		  ID  : /stonefs6/2013x2_project/workspace

		"""
		# first create the workspace
		parent = '/stonefs%d/%s' % (partition,project)
		self._create_node(parent,'WORKSPACE',workspace)

	def create_desktop(self,partition,project,workspace,name):
		"""
		/stonefs6/2013x2_project/workspace/DESKTOP
		<BinEntry><Name>DESKTOP</Name><WriteCompatible>True</WriteCompatible><Locked>False</Locked></BinEntry>

		  NAME: Desktop
		  TYPE: BINENTRY
		  ID  : /stonefs6/2013x2_project/workspace/DESKTOP

		"""
		parent = '/stonefs%d/%s/%s' % (partition,project,workspace)
		node_name = name
		node_type = 'BINENTRY'
		#xml_str = "<BinEntry><Name>DESKTOP</Name><WriteCompatible>True</WriteCompatible><Locked>False</Locked></BinEntry>"
		self._create_node(parent,node_type,node_name)
	
	def create_library(self,partition,project,library):
		"""
		/stonefs6/2013x2_project/workspace/DESKTOP/editing
		<Library><Name>editing</Name><WriteCompatible>True</WriteCompatible><Locked>False</Locked><LastModified>1364510901</LastModified><LastModifiedStr>2013-03-28 15:48:21</LastModifiedStr></Library>

		  NAME: editing
		  TYPE: LIBRARY
		  ID  : /stonefs6/2013x2_project/workspace/DESKTOP/editing

		"""
		parent = '/stonefs%d/workspace/%s' % (partition,project)
		node_name = library
		node_type = 'LIBRARY'
#		xml_str = "<Library><Name>editing</Name><WriteCompatible>True</WriteCompatible><Locked>False</Locked><LastModified>1364510901</LastModified><LastModifiedStr>2013-03-28 15:48:21</LastModifiedStr></Library>"
		print 'self._create_node(',parent,node_type,node_name
		self._create_node(parent,node_type,node_name)



	###################################
	#
	#	2013 wiretap functions
	#
	###################################
	def create_user(self,partition,user):
		partition = 'stonefs%d' % partition
		xmlstream ="<User>"
		xmlstream += "<Name>%s</Name>" % user
		xmlstream += "</User>"
		parent = '/%s/users' % (partition)
		#return self._create_node(parent, 'USER', user, xmlstream=xmlstream)
		self._create_node(parent,'USER',user,xmlstream=xmlstream)


	def create_project(self,partition,dl_project_name):
		"""
		Check for this project on the framestore. Create a new project
		if one does not already exist, setting attributes according to
		width,height,bitdepth, and aspect. --- OR --- check / reset the 
		attributes for a current project if one already exists
		"""
		# create the xml stream with the settings
		#template = '/usr/discreet/io/2013.2.2/templates/'
		partition = 'stonefs%d' % partition
		template = '/Volumes/discreet/templates/2013.2.2/flame'
		setup_dir = '/usr/discreet/tmp/setups'
		source_cfg = '/Volumes/discreet/templates/2013.2.2/project_cfg/1920x1080@23976psf.cfg'
		proj_path = '%s/%s' % (setup_dir,dl_project_name)
		lcl_proj_path = '/usr/discreet/project/%s' % (dl_project_name)
		cfg_path = '%s/%s/cfg' % (setup_dir,dl_project_name)
		dest_cfg = '%s/%s.cfg' % (cfg_path,dl_project_name)
		fileutil.makedirs(cfg_path)
		shutil.copyfile(source_cfg,dest_cfg)
		fileutil.makedirs('/usr/discreet/project/%s' % dl_project_name)

		command = 'rsync -a %s/ %s/' % (template,proj_path)
		stdin = commands.getoutput(command)
		
		xmlstream ="<Project>"
		xmlstream+="<Description>Wiretap tests</Description>"
#		xmlstream+="<SetupDir>%s</SetupDir>" % proj_path
		xmlstream+="<FrameWidth>1920</FrameWidth>"
		xmlstream+="<FrameHeight>1080</FrameHeight>"
		xmlstream+="<FrameDepth>10-bit</FrameDepth>"
		xmlstream+="<AspectRatio>1.7777</AspectRatio>"
     		xmlstream+="<VisualDepth>12-bit</VisualDepth>"
		xmlstream+="<ProxyEnable>false</ProxyEnable>"
		xmlstream+="<ProxyWidthHint>960</ProxyWidthHint>"
		xmlstream+="<ProxyDepthMode>SAME_AS_HIRES</ProxyDepthMode>"
		xmlstream+="<ProxyMinFrameSize>960</ProxyMinFrameSize>"
		xmlstream+="<ProxyAbove8bits>false</ProxyAbove8bits>"
		xmlstream+="<ProxyQuality>lanczos</ProxyQuality>"
		xmlstream+="<FieldDominance>PROGRESSIVE</FieldDominance>"
		xmlstream+="</Project>"

		# strange wiretap bug? 
		# if the SetupDir tag is in the xml we get this error:
		# Error setting xmlstream: Cannot open default config file '/usr/discreet/io/2013.2.2/templates/cfg/linux-x86_64/template/ntsc.cfg'
		# ...and the project.db lists the default setupdir for the location regardless
#		fileutil.makedirs('/usr/discreet/io/2013.2.2/templates/cfg/linux-x86_64/template')
#		odd_cfg = '/usr/discreet/io/2013.2.2/templates/cfg/linux-x86_64/template/ntsc.cfg'
#		shutil.copyfile(source_cfg,odd_cfg)
#		open('/usr/discreet/io/2013.2.2/templates/cfg/linux-x86_64/template/ntsc.cfg','a').close()

		self._create_node(partition,'PROJECT',dl_project_name,xmlstream=xmlstream)

		# remove the newly created empty project directory and link it to our 
		# real setup location
		os.removedirs(lcl_proj_path)
		os.symlink(proj_path,lcl_proj_path)

		#xmlstream ="<SetupDir>%s</SetupDir>" % proj_path
		#new_node = WireTapNodeHandle(self.server,"/%s/%s" % (partition,dl_project_name))
		#new_node.setMetaData("XML",xmlstream)

	def create_shared_library(self,partition,project,library):
		# first create the workspace
		parent = '/stonefs%d/%s' % (partition,project)
		self._create_node(parent,'WORKSPACE',library)

	def create_subfolder(self,partition,project,library,subfolder):
		"""
		+ nodeID => /stonefs7/proj07/WT_LIB01/MEDIA_LIBRARY/dir01
		+ type => LIBRARY
		"""
		parent = '/stonefs%d/%s/%s/MEDIA_LIBRARY' % (partition,project,library)
		self._create_node(parent,'LIBRARY',subfolder)



if __name__ == '__main__':
	w = Wiretap('flame02')
	print_array(w._get_children('stonefs4/13E542-Nike_Id/kevins/MEDIA_LIBRARY'))
#	print_array(w._get_children('stonefs4/workspace_test/workspace3/MEDIA_LIBRARY'))
#	w.create_subfolder(1,'2013_2_53_proj01','hacker','Default Library')

	# NOTES: Creating a project is still pretty straight forward
	#        Creating a shared library is weird though. You create
	#	   a 'workspace' which is what a shared library really is.
#	w.create_project(7,'proj07')
#	w.create_shared_library(7,'proj07','WT_LIB02')
#	w.create_subfolder(7,'proj07','WT_LIB02','sf02')
#	w.create_subfolder(7,'proj07','WT_LIB02','sf03')
#	w.create_subfolder(7,'proj07','WT_LIB02','sf04')
#	w.create_subfolder(7,'proj07','WT_LIB02','sf05')
#	w.create_user(5,'wt_user01')


#	w.create_desktop(7,'proj07','workspace','Desktop')
#	w.create_library(7,'proj07','WT_LIB01')

#	print w._get_metadata(node='/stonefs6/2013_wiretap_project_01')
#	print w._get_metadata(node='/stonefs6/2013x2_project')
	
#	parent = '/stonefs6/2013_wiretap_project_01'
#	w._create_node(parent,'WORKSPACE','wt_workspace')

	#parent = '/stonefs6/2013x2_project'
	#parent = '/stonefs6/2013x2_project/workspace'
	#parent = '/stonefs6/2013x2_project/workspace/DESKTOP'
	#parent = '/stonefs6/2013x2_project/workspace/DESKTOP/editing'

#	parents = [	'/stonefs6/2013x2_project',
#			'/stonefs6/2013x2_project/workspace',
#			'/stonefs6/2013x2_project/workspace/DESKTOP',
#			'/stonefs6/2013x2_project/workspace/DESKTOP/editing']
#	for p in parents:
#		print 
#		print "-"*120
#		print p
#		print w._get_metadata(p)
#		child = WireTapNodeHandle(w.server,"/%s" % p.strip("/"))
#		name = w._get_node_name(child)
#		typeStr = w._get_node_type(child)
#		nodeID = WireTapStr( child.getNodeId().id() )
#		print "  NAME:",name
#		print "  TYPE:",typeStr
#		print "  ID  :",nodeID.c_str()

#	w._create_node(parent,'WORKSPACE','rogue_workspace')

#	parent = '/stonefs5/flare_local'
#	#children = w._get_children(node='/stonefs6/2013_wiretap_project_01')
#	children = w._get_children(node=parent)
#	for node in children:
#		print "%s: %s" % (children[node]['type'],children[node]['name'])
#		print "-"*50
#		print_array(children[node])



	# NOTE: seems like without disconnecting we get a random segfault
	#w._disconnect()
	pass


