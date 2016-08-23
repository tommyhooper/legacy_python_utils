#!/usr/bin/env python

import glob
import re
import os
import socket
import datetime
import traceback
from A52.utils import print_array
from A52.utils import numberutil
from A52 import settings
from A52 import environment
from A52.Project import Project
from A52.Framestore import Framestore
from A52 import utils

import logging
log = logging.getLogger(__name__)

CONTEXT = environment.get_context()

class dlProject:
	"""
	Main class to manipulate the Framestore class
	"""
	FRAMEDEPTHS = {	'8 bit':'8-bit',
				'10 bit':'10-bit',
				'12 bit':'12-bit',
				'12 bit unpacked':'12-bit u'}
	GFXDEPTHS = {	'8-bit graphics':'8-bit',
				'16-bit graphics':'12-bit'}
	PROXYMODES = {		0:{'name':'Proxies Off','mode':'off'},
					1:{'name':'Proxies On','mode':'on'},
					2:{'name':'Conditional','mode':'conditional'}}
	PROXYQUALITIES = {	0:{'name':'Lanczos','value':'lanczos'},
					1:{'name':'Shannon','value':'shannon'},
					2:{'name':'Gaussian','value':'gaussian'},
					3:{'name':'Quadratic','value':'quadratic'},
					4:{'name':'Bicubic','value':'bicubic'},
					5:{'name':'Mitchel','value':'mitchel'},
					6:{'name':'Triangle','value':'triangle'},
					7:{'name':'Impulse','value':'impulse'},
					8:{'name':'Draft','value':'draft'}}
	PROXYWIDTHHINTS = {	0:{'name':'Fixed Width','mode':'fixed'},
					1:{'name':'Frame Percentage','mode':'percentage'}}
	PROXYDEPTHMODES = {	0:{'name':'8 bit','value':'8-bit'},
					1:{'name':'Same bitdepth as clip','value':'SAME_AS_HIRES'}}

	RANGES = 	{	'FrameWidth':(24,8192),
				'FrameHeight':(24,8192),
				'AspectRatio':(0.001,100.0),
				'ProxyWidthHint':(0.01,8192.0),
				'ProxyMinFrameSize':(0,8192)
			}

	CHOICES = {		'ProxyEnable':['true','false'],
				'ProxyDepthMode':['8-bit','SAME_AS_HIRES'],
				'ProxyAbove8bits':['true','false'],
				'FieldDominance':['FIELD_1','FIELD_2','PROGRESSIVE'],
				'VisualDepth':['8-bit','12-bit','unknown']
			}

	DEFAULTS = {	'cfg_file':'1920x1080@23976psf.cfg',
				'FrameWidth':1920,
				'FrameHeight':1080,
				'FrameDepth':'10-bit',
				'AspectRatio':'1.778',
				'ProxyEnable':'false',
				'ProxyWidthHint':'960',
				'ProxyDepthMode':'SAME_AS_HIRES',
				'ProxyMinFrameSize':960,
				'ProxyAbove8bits':'false',
				'ProxyQuality':'lanczos',
				'FieldDominance':'PROGRESSIVE',
				'VisualDepth':'12-bit',
				'SetupDir':'',
				'Description':''
			}

	def __init__(self,host,volume,project_name,**kwargs):
		"""
		DL Project Object
		"""
		self.host = host
		self.volume = volume
		self.project_name = project_name
		self.data = DEFAULTS
		self.data.update(kwargs)
		self.default = settings.DL_PROPERTIES[CONTEXT]
		self.framestore = Framestore(host=host,volume=volume)
		# mode is either 'project' or 'settings'
		# 'settings' mode cannot be saved or created
		self.mode = 'project'

	def __getattr__(self,name):
		"""
		Catch specific attributes if they are
		used before they are set and set them here
		for convenience
		"""
		#if name == 'dl_basename':
		#	project = Project.find(uid=self.data['project_uid'])[0]
		#	return "%s-%s" % (project.data['job_num'],project.data['name'])
		#if name == 'framestore':
		#	return Framestore.find(uid=self.data['framestore_uid'])[0]
		if name == 'version_short':
			version_short = self.get_version_short()
			if version_short:
				self.version_short = version_short
				return self.version_short
		if name == 'localhost':
			hostname = socket.gethostname()
			if hostname:
				self.localhost = hostname
				return self.localhost
		message = "'dlProject' object has no attribute '%s'" % name
		raise AttributeError,message

	def get_version_short(self):
		if self.data.has_key('version'):
			return re.search('^([0-9]{4}).*$',self.data['version']).group(1)
		return False
	
	def create_directories(self,software_type,rsync=True):
		"""
		This function is used to create the directory
		tree for new projects, or check the tree for
		existing projects.
		NOTE: the wiretap API will create this tree when 
		the project is created. In theory that would mean
		this function is obsolete, however... so far it 
		looks like the wiretap projcet trees are missing 
		the files in 'substance/presets' (the directories 
		are there but no actual textures).
		"""
		# create the main project directory
		project_dir = "%s/%s" % (self.default['project_setup_home'],self.dl_basename)
		log.info("mkdir %s" % project_dir)
		#utils.makedirs(project_dir)
		if rsync:
			# rsync the template to the main project location
			# --chmod=ugo=rwX
			command = "rsync -a %s/%s/project/%s/ %s/" % (	self.default['template_dir'],
											self.version_short,
											software_type,
											project_dir)
			print "Syncing project template: %s" % command
 			#success = os.system(command)
		return
		# create the local project tree base on the host and it's cfg directory
		# also create a batch directory in the local tree - I suspect it is still 
		# used for the user 'bin' setups (it's ignoring the cfg file)
		local_project_home = "/hosts/%s/usr/discreet/project/%s" % (self.host,self.project_name)
		log.info("makedirs %s" % local_project_home)
		log.info("makedirs %s/cfg" % (local_project_home))
		log.info("makedirs %s/batch" % (local_project_home))
		#utils.makedirs(local_project_home)
		#utils.makedirs("%s/cfg" % local_project_home)
		#utils.makedirs("%s/batch" % local_project_home)

	def create_host_linkbacks(self,software_type):
		"""
		In each module, link the software 'type' back up one directory.
		this effectively cheats our way around the new 'type' directory 
		that the flame adds to each module
		"""
		# these links cannot or should not have a link back in them
		exclude_links = ['import','export','lut']
		# get a list of modules from the main project tree
		project_dir = "%s/%s" % (self.default['project_setup_home'],self.dl_basename)
		modules = glob.glob("%s/*" % project_dir)
		for module in modules:
			module_name = os.path.basename(module)
			if not module_name in exclude_links:
				if os.path.isdir(module):
					link = "%s/%s_%s" % (module,software_type,self.localhost)
					#log.info("symlink('.',%s)" % link)
					#utils.symlink(".",link)
					# the local machine makes a software-only directory
					if self.host == self.localhost:
						link = "%s/%s" % (module,software_type)
						log.info("symlink('.',%s)" % link,3)
						#utils.symlink(".",link)

	def create_project_links(self):
		"""
		Create links from the project tree to relevant areas
		in the main project tree.
		"""
		project_base = "%s/%s" % (self.default['project_setup_home'],self.dl_basename)
		link_base = "/hosts/%s/usr/discreet/project/%s" % (self.host,self.project_name)

		# TODO: this may not be necessary to keep around
		# check for lingering batch links and remove them
		target = "%s/%s" % (link_base,'batch''batch')
		if os.path.islink(target):
			print "Removing batch link"
			#try: os.remove(target)
			#except:pass

		# make sure the link base exists
		#utils.makedirs(link_base)
		directories = ['monitor','tmp','gmask','path','status','sparks','batch/pref','filter']
		# link project directories (the symlink method will move existing directories aside)
		for directory in directories:
			log.info("utils.symlink('%s/%s','%s/%s)" % (project_base,directory,link_base,directory),3)
			#utils.symlink('%s/%s' % (project_base,directory),'%s/%s' % (link_base,directory))

	def create_project_cfg(self):
		"""
		Create the project cfg by taking the template that
		the user chose and replacing the module home directories
		"""
		# first grab the lines of the choosen config file
		template_file = '%s/%s/project_cfg/%s' % (self.default['template_dir'],self.version_short,self.data['cfg_file'])
		if not os.access(template_file,os.R_OK):
			# cfg file does not exist
			message = "Error: Could not find cfg_file: %s" % template_file
			raise Exception,message
		f = open(template_file,'r')
		lines = f.readlines()
		template_lines = []
		for line in lines:
			#log.info(">> %s" % line.strip('\n'))
			if re.match('^#.*',line) or line == '\n':
				# commented or empty line - skip it...
				pass
			elif '~' in line:
				# home directory line - skip it...
				pass
			else:
				template_lines.append(line.strip('\n'))
		f.close()

		# move the original cfg file aside (only the original)
		project_cfg_dir = "/hosts/%s/usr/discreet/project/%s/cfg" % (self.host,self.project_name)
		project_cfg = "%s/%s.cfg" % (project_cfg_dir,self.project_name)
		if not os.access(project_cfg_dir,os.R_OK):
			log.info("utils.makedirs(%s)" % (project_cfg_dir),3)
			#utils.makedirs(project_cfg_dir)
		if not os.access(project_cfg+'.ori',os.R_OK):
			# if there is no .ori file, move the current cfg aside
			# if there is one then we assume we've already backed up
			# the 'original' cfg and just overwrite the current one
			try:
				log.info("Moving original cfg aside: %s --> %s.ori" % (project_cfg,project_cfg))
				#os.rename(project_cfg,project_cfg+'.ori')
			except: pass

		# open the new cfg file
		cfg = open(project_cfg,'w')
		# add the non module home lines from the original cfg
		for line in template_lines:
			#log.info("TEMPLATE: %s" % line)
			cfg.write(line+'\n')
		# now add the module homes
		modules = self.get_cfg_module_homes()
		for index in modules['cfg_lines']:
			#log.info("MODULE: %s" % modules['cfg_lines'][index])
			cfg.write(modules['cfg_lines'][index]+'\n')
		cfg.close()
		try: os.chmod(project_cfg,0777)
		except:pass

	def get_cfg_module_homes(self):
		"""
		Get the module home definitions from a cfg file.
		Module home lines in the cfg file look like:
			Batch	 ~/batch,		 batch
		We replace the '~' with our project home directory.
		(dl_project_name).
		"""
		# there are a few module lines in the cfg file that we do not replace with the home directory
		# 'ignored' are lines that the flame ignores for whatever reason (but we still put them in the cfg)
		# 'dl_base' are lines that we point to one location regardless of project
		# 'dl_share' are lines that we point to one location within a project but regardless of user
		#	       (we are not using the user level so dl_share will be unused for now)
		ignored = ['desktop','guides','hotkey','play','documentation']
		undocumented = ['path','status']
		dl_base = []
		dl_share = []
		template_file = '%s/%s/project_cfg/%s' % (self.default['template_dir'],self.version_short,self.data['cfg_file'])
		# get the target cfg file 
		if not os.access(template_file,os.R_OK):
			# cfg file does not exist - fall back on a default cfg file
			template_file = '%s/%s/project_cfg/film.cfg' % (self.default['template_dir'],self.version_short)
			log.info("CFG file not found: %s" % cfg_file)
			log.info("Using default cfg for module homes: %s" % template_file)
		f = open(template_file,'r')
		lines = f.readlines()
		module_lines = []
		for line in lines:
			#log.info(">> %s" % line.strip('\n'))
			if re.match('^#.*',line) or line == '\n':
				# commented or empty line - skip it...
				pass
			elif '~' in line:
				# home directory line, check for exceptions
				module_lines.append(line.strip('\n'))
			else:
				# all other lines - skip
				pass
		f.close()
		modules = {'directories':{},'cfg_lines':{}}
		project_dir = "%s/%s" % (self.default['project_setup_home'],self.dl_basename)
		i = 1
		for line in module_lines:
			directory = re.search("^.*(~\/[0-9A-z]+).*",line).group(1)
			module = directory.split("/")[1]
			line_type = 'default'
			# check for base, or shared lines (see __init__)
			for ex in dl_base:
				if re.match('.*%s.*' % ex,line):
					line_type = 'dl_base'
					modules['cfg_lines'][i] = line.replace('~',self.default['dl_base'])
					modules['directories'][i] = {module:directory.replace('~',self.default['dl_base'])}
			for ex in dl_share:
				if re.match('.*%s.*' % ex,line):
					line_type = 'dl_share'
					modules['cfg_lines'][i] = line.replace('~',self.default['dl_share'])
					modules['directories'][i] = {module:directory.replace('~',self.default['dl_share'])}
			for ex in ignored:
				if re.match('.*%s.*' % ex,line):
					line_type = 'ignored'
					modules['cfg_lines'][i] = line
					#modules['directories'][i] = {module:directory.replace('~',self.default['dl_share'])}
			if line_type is 'default':
				modules['cfg_lines'][i] = line.replace('~',project_dir)
				modules['directories'][i] = {module:directory.replace('~',project_dir)}
			i+=1
		# manually add the undocumented modules we have to deal with
		for directory in undocumented:
			modules['directories'][i] = {module:"%s/%s" % (project_dir,directory)}
			i+=1
		return modules
			
	def cheat_status(self,dl_home):
		"""
		Pre-edit the cotents of the LastFramestoreAndProject.pref
		in the software home's status directory. 
		"""
		fl = open("%s/status/LastFramestoreAndProject.pref" % (dl_home),'w')
		fl.write("%s/%s\n" % (self.volume,self.host))
		fl.write("%s\n" % self.project_name)
		#fl.write("LocalUserDB\n")
		fl.write("RemoteUserDB\n")
		fl.close()

	def parse_project_name(name):
		"""
		Split a dl_project name into 
		4 parts:
			production uid
			job_num
			project_name
			extension
		"""
		regx = re.compile('.*([0-9]{2}[A-Z][0-9]{3})[-_]*(.*)(_[A-Z,a-z]*)$')
		try:
			job_num,project_name,ext = regx.search(name).groups()
		except:
			return (None,'misc',name,None)
		return (job_num,project_name,ext)
	parse_project_name = staticmethod(parse_project_name)

	def get_cfg_files(self):
		"""
		Get the project cfg files
		"""
		cfg_dir = '%s/%s/project_cfg' % (self.default['template_dir'],self.version_short)
		os.chdir(cfg_dir)
		cfg_files = glob.glob('*.cfg')
		return cfg_files

	##
	## FROM MODELS ##
	##
	def create_library(self,library):
		"""
		Create a new library on this framestore
		"""
		dl_project_name = self.project_name
		libraries = self.framestore.get_libraries(dl_project_name)
		libs = []
		for lib in libraries:
			libs.append(libraries[lib]['name'])
		# create each lib if it doesn't already exist
		if not library in libs:
			print "Creating: %s" % library
			self.framestore.create_library(dl_project_name,library)
		return True

	def create_libraries(self,library_list):
		"""
		Create a new library on this framestore
		for each library in 'library_list'
		"""
		if type(library_list) is not list:
			library_list = [library_list]
		dl_project_name = self.data['name']
		libraries = self.framestore.get_libraries(dl_project_name)
		existing_libs = []
		for lib in libraries:
			existing_libs.append(libraries[lib]['name'])

		create_libs = []
		for lib in library_list:
			if lib not in existing_libs:
				create_libs.append(lib)
		if create_libs:
			print "Creating libraries: %s" % repr(create_libs)
			self.framestore.create_library(dl_project_name,create_libs)
		return True

	def _create_project(self):
		"""
		Check for this project on the framestore. Create a new project
		if one does not already exist, setting attributes according to
		width,height,bitdepth, and aspect. --- OR --- check / reset the 
		attributes for a current project if one already exists
		
		API DANGERS:
		-	When creating a project, if you set the SetupDir to an
			existing projects SetupDir, the project settings are
			ignored.
		- 	If the ProxyMinFrameSize is less than the
			ProxyWidthHint and the proxy mode is set to 'fixed',
			the project settings are ignored again.
		OTHER DANGERS:
		-	This has to do with the project's cfg file, not the
			wiretap API, but I'm mentioning it here because it 
			makes sense categorically:
			When setting the module homes, a few of the ~ lines
			refer to the software directory (/usr/discreet/flame_2011.1)
			and NOT the project setup directory. Most importantly,
			the HotKey line must either point to a software install
			directory or be left as it's default ~/hotkey, hotkey. 
			This directory is where the default keybinds are set
			(i.e. the collapse 'c' key for clips on the desktop)
		"""
		settings = self.data
		dl_project_name = settings['name']

		# check to see if this project exists or not
		if self.framestore.find_project(dl_project_name=dl_project_name):
			# project already exists
			log.info("Project %s exists" % (dl_project_name))
			return 'Exists'
		else:
			log.info("Project %s is new, creating..." % (dl_project_name))
			# create the xml stream with the settings
			xmlstream ="<Project>"
			xmlstream+="<Description>Project created by Fuse</Description>"
			# we DO NOT want the flame to know where our setups are
			#xmlstream+="<SetupDir>%s</SetupDir>" % (settings['SetupDir'])
			xmlstream+="<FrameWidth>%s</FrameWidth>" % (settings['FrameWidth'])
			xmlstream+="<FrameHeight>%s</FrameHeight>" % (settings['FrameHeight'])
			xmlstream+="<FrameDepth>%s</FrameDepth>" % (settings['FrameDepth'])
			xmlstream+="<AspectRatio>%s</AspectRatio>" % (settings['AspectRatio'])
     			xmlstream+="<VisualDepth>%s</VisualDepth>" % (settings['VisualDepth'])
			xmlstream+="<ProxyEnable>%s</ProxyEnable>" % (settings['ProxyEnable'])
			xmlstream+="<ProxyWidthHint>%s</ProxyWidthHint>" % (settings['ProxyWidthHint'])
			xmlstream+="<ProxyDepthMode>%s</ProxyDepthMode>" % (settings['ProxyDepthMode'])
			xmlstream+="<ProxyMinFrameSize>%s</ProxyMinFrameSize>" % (settings['ProxyMinFrameSize'])
			xmlstream+="<ProxyAbove8bits>%s</ProxyAbove8bits>" % (settings['ProxyAbove8bits'])
			xmlstream+="<ProxyQuality>%s</ProxyQuality>" % (settings['ProxyQuality'])
			xmlstream+="<FieldDominance>PROGRESSIVE</FieldDominance>"
			xmlstream+="</Project>"
			log.info("Creating project")
			log.info("XML: %s" % xmlstream)
			self.framestore.create_project(dl_project_name,xmlstream)
			return 'New'
		return True


if __name__ == '__main__':
#	print dlProject.direct_du(host='flame01',volume='stonefs4',dl_project_name='11A163-Nescafe_Hypnotist_MASTER')
#	stat_obj = dl_project_stats.find(host='smoke01',volume='stonefs4',dl_project_name='11A137-Gatorade_Billions_CamCoombs')
#	stat_obj[0].inspect()
#	d = dlProject.find(name='11A163-Nescafe_Hypnotist_MASTER')[0]
#	d.inspect(filter='full')


	names = {}
	for obj in dlProject.find():
		try:
			names[obj.data['name']].append(obj)
		except:
			names[obj.data['name']] = [obj]

	def diff_objs(objs):
		skip = ['uid','SetupDir','creation_date','framestore_uid']
		first = objs[0]
		for key in first.data.keys():
			if key in skip:
				continue
			for obj in objs[1:]:
				if first.data[key] != obj.data[key]:
					return (key,first.data[key],obj.data[key])
		return False

	for name,objs in names.iteritems():
		if len(objs) > 1:
			diff = diff_objs(objs)
			if diff:
				print "[44m%s[m  %s" % (name,diff)
				#print "-"*80

				
				#for obj in objs:
				if False:
					print "%3s%7s%15s%7s%5s%5s%6s%14s%6s%4s%8s%4s%7s%23s%3s%7s%3s%8s%9s" % (
					obj.data['uid'],
					obj.data['AspectRatio'],
					obj.data['FieldDominance'],
					obj.data['FrameDepth'],
					obj.data['FrameHeight'],
					obj.data['FrameWidth'],
					obj.data['ProxyAbove8bits'],
					obj.data['ProxyDepthMode'],
					obj.data['ProxyEnable'],
					obj.data['ProxyMinFrameSize'],
					obj.data['ProxyQuality'],
					obj.data['ProxyWidthHint'],
					obj.data['VisualDepth'],
					obj.data['cfg_file'],
					obj.data['framestore_uid'],
					obj.data['project_class'],
					obj.data['project_uid'],
					obj.data['user_id'],
					obj.data['version'])



