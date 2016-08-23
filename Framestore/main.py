#!/usr/bin/env python

import glob
import os
import stat
import sys
import time
import re
import traceback
import Queue
import threading
import commands
from datetime import datetime
from wiretap import Wiretap
from A52.utils import print_array
from A52.utils import diskutil
from A52.utils import numberutil
from A52.utils import fileutil
from A52.dlLibrary import dlLibrary

class FramestoreException(Exception):
	pass

class Framestore(object,Wiretap):
	"""
	Main class to manipulate the Framestore class
	"""
	FRAMESTORES = {	'conform01':{	4:	{
								'name':'SANSTONE08',
								'path':'/Volumes/F5412SATA02/conform01/p4'
								}
						},

				'flame01':	{	4:	{
								'name':'SANSTONE01',
								'path':'/Volumes/F6500SAS01/flame01/p4'
								},
							5:	{
								'name':'SANSTONE10',
								'path':'/Volumes/F6500SAS02/flame01/p5'
								}
						},
				'flame02':	{	4:	{
								'name':'SANSTONE02',
								'path':'/Volumes/F6412SAS05/flame02/p4'
								},
							5:	{
								'name':'SANSTONE09',
								'path':'/Volumes/F6500Rental02/flame02/p5'
								}
						},
				'flame03':	{	4:	{
								'name':'SANSTONE03',
								'path':'/Volumes/F6412SAS04/flame3/p4'
								}
						},
				'flame04':	{	4:	{
								'name':'SANSTONE04',
								'path':'/Volumes/F6412SAS03/flame04/p4'
								}
						},
				'flame06':	{	4:	{
								'name':'SANSTONE11',
								'path':'/Volumes/DH3723SAS01/flame06/p4'
								}
						},
				'smack01':	{	4:	{
								'name':'SANSTONE06',
								'path':'/Volumes/F5412SATA01/smack01/p4'
								}
						},
				'smoke01':	{	4:	{
								'name':'SANSTONE05',
								'path':'/Volumes/F6412SAS02/smoke01/p4'
								},
							5:	{
								'name':'SANSTONE07',
								'path':'/Volumes/F6500Rental01/smoke01/p5'
								}
						},
				}


	def __init__(self,host,partition):
		# run the wiretap init
		#super(Framestore,self).__init__()
		self.host = host
		self.partition = partition
		self.volume = 'stonefs%d' % partition
		self.name = self.FRAMESTORES[host][partition]['name']
		self.path = self.FRAMESTORES[host][partition]['path']
		self.locks = {}
		# stat objects for each project:
		self.pstats = {}
		self.pstat_totals = {
			'frames_self':0,
			'frames_shared':0,
			'frames_total':0,
			'bytes_self':0,
			'bytes_shared':0,
			'bytes_total':0,
			'dsp_bytes_self':'',
			'dsp_bytes_shared':'',
			'dsp_bytes_total':'',
		}
		# stat dictionaries for project groups
		self.pstat_groups = {}

	def __getattr__(self,name):
		if name == 'bytes_used':
			self.format_df()
			return self.bytes_used
		if name == 'bytes_free':
			self.format_df()
			return self.bytes_free
		if name == 'bytes_total':
			self.format_df()
			return self.bytes_total
		if name == 'dsp_bytes_used':
			self.format_df()
			return self.dsp_bytes_used
		if name == 'dsp_bytes_free':
			self.format_df()
			return self.dsp_bytes_free
		if name == 'dsp_bytes_total':
			self.format_df()
			return self.dsp_bytes_total
		if name == 'percent_used':
			self.format_df()
			return self.percent_used
		if name == 'fraction_used':
			self.format_df()
			return self.fraction_used
		return super(Framestore,self).__getattr__(name)
		#message = "'%s' has no attribute %s" % (__name__,name)
		#raise AttributeError,message
	
	def scan_libraries(self):
		"""
		Scan libraries and sync them
		to the database.
		"""
		# build a list of libraries
		# found on the filesystem
		fs_list = []
		host = self.host
		volume = self.volume
		proj_home = '/hosts/%s/usr/discreet/clip/%s' % (host,volume)
		projects = glob.glob('%s/*' % proj_home)
		for project in projects:
			project_name = os.path.basename(project)
			# scan for libraries
			libs = glob.glob('%s/*.000.clib' % (project))
			for lib in libs:
				library_name = os.path.basename(lib)
				mod_date = fileutil.mod_date(lib)
				fs_list.append((project_name,library_name,mod_date))

		# build an array of libraries
		# found in the db
		db_array = dlLibrary.get_libraries(host=host,volume=volume)

		# reset the refcounts
		dlLibrary.reset_refcounts(host,volume)

		# insert / update db records
		for project,lib,mod_date in fs_list:
			if not dlLibrary.is_excluded(lib):
				try:
					uid = db_array[project][lib]['uid']
					dlLibrary.update_mod_date(uid,mod_date)
				except:
					obj = dlLibrary(	host=host,
								volume=volume,
								project=project,
								name=lib,
								date_modified=mod_date,
								refcount=1)
					obj.save()

		# purge zero refcount libraries
		dlLibrary.purge_refcounts(host,volume)

	def get_libraries(self,dl_project_name,source='wiretap'):
		"""
		Get the libraries for 'dl_project' on the framestore
		"""
		parent = "%s/%s" % (self.volume,dl_project_name)
		return self._get_children(node=parent,node_type='LIBRARY')

	def get_users(self,source='wiretap'):
		"""
		Get the users on the framestore
		if source is 'db' get the users from the db
		"""
		editing = self._get_children(node='/%s/users/editing' % self.volume,node_type='USER')
		effects = self._get_children(node='/%s/users/effects' % self.volume,node_type='USER')
		users = {'editing':{},'effects':{}}
		for i in editing:
			users['editing'][i] = editing[i]
		for i in effects:
			users['effects'][i] = effects[i]
		return users

	def get_projects(self,source='wiretap'):
		"""
		Get the projects on the framestore
		"""
		if source == 'wiretap':
			return self._get_children(node=self.volume,node_type='PROJECT')
		elif source == 'db':
			# in order to find the current projects from the db we 
			# need to use the dl_libraries table since that is 
			# kept up to date
			#return dlProject.find(framestore_uid=self.data['uid'])
			return dlLibrary.get_current_projects(host=self.host,volume=self.volume)

	def find_project(self,dl_project_name):
		"""
		Get the projects on the framestore
		"""
		nodes = self._get_children(node=self.volume,node_type='PROJECT')
		if type(nodes) is tuple:
			return nodes
		projects = []
		for i in nodes:
			if nodes[i]['name'] == dl_project_name:
				return nodes[i]
		return None

	def find_user(self,category,user):
		"""
		Find 'user' on the framestore.
		Searches under both categories 
		('effects' and 'editing')
		"""
		parent = "%s/users/%s" % (self.volume,category)
		print "\nSearching for %s on /%s/%s %s\n" % (user,self.host,parent,'USER')
		nodes = self._get_children(node=parent,node_type='USER')
		if type(nodes) is tuple:
			return nodes
		for i in nodes:
			if nodes[i]['name'] == user:
				print "Found user %s" % nodes[i]['name']
				return nodes[i]
		return None

	def create_user(self,user_category,user,xmlstream):
		"""
		Create a user on the given framestore
		"""
		# create the user node
		parent = "/%s/users/%s" % (self.volume.strip('/'),user_category)
		return self._create_node(parent,'USER',user,xmlstream=xmlstream)

	def create_project(self,dl_project_name,xmlstream):
		"""
		Create a project on the given framestore
		"""
		# create the project node
		return self._create_node(self.volume,'PROJECT',dl_project_name,xmlstream=xmlstream)

	def create_library(self,dl_project_name,library):
		"""
		Create a library 'library' for the project 'dl_project_name' on this framestore
		"""
		# create the project node
		parent = "%s/%s" % (self.volume,dl_project_name)
		return self._create_node(parent,'LIBRARY',library)

	def create_library(self,dl_project_name,library):
		"""
		Create a library for the given project.
		If the library exists nothing new will happen.
		"""
		parent = "/%s/%s" % (self.volume,dl_project_name)
		return self._create_node(parent,'LIBRARY',library)

	def df(self,mount_base=None):
		"""
		Get the disk free for this framestore.
		'mount_base' can be specified if the df
		is going through a different mount point
		such as an automount path. 
		e.g. /hosts/meta01/Volumes/...
		"""
		# mount name
		if mount_base:
			mount_dir = "/%s/Volumes/%s" % (mount_base,self.data['mount_name'])
		else:
			mount_dir = "/Volumes/%s" % (self.data['mount_name'])
		if not os.path.exists(mount_dir):
			raise FramestoreException,"Mount path does not exist: %s" % mount_dir
		df = diskutil.df(mount_dir)
		self.data['bytes_total'] = df['bytes_total']
		self.data['bytes_free'] = df['bytes_free']
		return df

	#@staticmethod
	def get_stones(host=None):
		"""
		Get the stonefs nodes listed by the wiretap server
		for the host: 'host'.
		If 'host' is None all known hosts will be 
		listed.
		NOTE: not all nodes will be valid.
		"""
		fs = Framestore()
		objs = []
		if host:
			stones = fs._get_children()
			for stone in stones:
				cls = Framestore(host=host)
				for key in stones[stone]:
					if key == 'name':
						cls.data['volume'] = stones[stone][key]
				objs.append(cls)
		return objs
	get_stones = staticmethod(get_stones)

	def du(self,verbose=False):
		self._du_fs(verbose=verbose)
		#return self._du_db()

	def _du_fs(self,verbose=False):
		"""
		Estimate the 'total' size of each 'production' project on
		the framestore. This involves analyzing every user project
		for a specific project in one group.
		"""
		frame_map = FrameMap(Framestore=self)
		dlprojects = self.get_projects()
		for i,dlp in dlprojects.iteritems():
			if dlp['name'] == '12A142--Visa_100_Jesse':
				#print "PROJECT:",dlp['name']
				frame_map.add_project(dlp['name'])
#			frame_map.add_project(dlp['name'])
		start = datetime.today()
		frame_map.poll(verbose=verbose)
		end = datetime.today()
		delta = end-start
		#print "DELTA:",delta

	def get_clips(self,node):
		"""
		Get clips out of a library node.
		"""
		clips = []
		children = self._get_children(node)
		for x,y in children.iteritems():
			if y['type'] == 'REEL':
				clips.extend(self.get_clips(y['node']))
			elif y['type'] == 'CLIP':
				clips.append(y)
		return clips
	
	def get_refcount(self):
		"""
		Analyze the ref counts and see
		who has a lock on the framestore.
		"""
		reflog = '/hosts/%s/usr/discreet/clip/%s/.ref.log' % (self.data['host'],self.data['volume'])
		rec = '/hosts/%s/usr/discreet/clip/%s/.ref.rec' % (self.data['host'],self.data['volume'])
		locks = {}
		f = open(rec)
		for line in f.readlines():
			host,hexid,pid,utime,count,name = line.split()
			date = datetime.fromtimestamp(float(utime))
			if not locks.has_key(hexid):
				locks[hexid] = {	'name':name,
							'host':host,
							'count':int(count),
							'pid':pid,
							'log':{utime:int(count)}
							}
			else:
				locks[hexid]['count']+= int(count)
				locks[hexid]['log'][utime] = int(count)
		self.locks = locks
		return self.locks

	def show_locks(self):
		"""
		Show the current locks on this framestore.
		"""
		# get or update the current ref count
		self.get_refcount()
		if self.is_locked():
			print "\n%-28s%-16s%12s" % ('Locks on %s/%s' % (self.data['host'],self.data['volume']),'host','PID')
			print "-"*56
			for hexid,info in self.locks.iteritems():
				if info['count'] >=1:
					print "%-28s%-16s%12s" % (info['name'],info['host'],str(info['pid']).lstrip('0'))
			print "-"*56
		else:
			print "\nNo locks on %s/%s" % (self.data['host'],self.data['volume'])
	
	def is_locked(self):
		"""
		Return True if the framestore has an active lock
		and False if not.
		"""
		self.get_refcount()
		for hexid,info in self.locks.iteritems():
			if info['count'] >=1:
				return True
		return False


class StatThread(threading.Thread):


	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			frame_obj = self.queue.get()
			frame_obj.framestat()
			#print "  Stat:%s\r" % (frame_obj.path)
			self.queue.task_done()


class FrameMap:
	"""
	A full or partial representation
	of the media cache on a Framestore.
	"""

	def __init__(self,Framestore):
		self.Framestore = Framestore
		self.frames = {}
		self.projects = []
		self.tree = {}
		self.frame_count_self = 0
		self.frame_count_shared = 0
		self.bytes_self = 0
		self.bytes_shared = 0
		self.bytes_total = 0

	def __getattr__(self,name):
		if name == 'total_frames':
			return self.frame_count_self + self.frame_count_shared
		if name == 'total_bytes':
			return self.bytes_self + self.bytes_shared
		if name == 'dsp_bytes':
			total_bytes = self.bytes_self + self.bytes_shared
			return numberutil.humanize(total_bytes,scale='bytes')
		if name == 'dsp_bytes_self':
			return numberutil.humanize(self.bytes_self,scale='bytes')
		if name == 'dsp_bytes_shared':
			return numberutil.humanize(self.bytes_shared,scale='bytes')
		message = "'%s' has no attribute %s" % (__name__,name)
		raise AttributeError,message
	
	def add_project(self,project):
		"""
		Add a MappedProject to the FrameMap
		which will be polled for frame 
		counts and sizes.
		"""
		# see if we already have this project in the map
		if len([p for p in self.projects if p.full_project_name == project]) > 0:
			return
		# add a MappedProject to this FrameMap
		obj = MappedProject(project,self.Framestore,self)
		self.projects.append(obj)

	def poll(self,verbose=False):
		"""
		Get framecounts from the wiretap server
		and get stats on each frame discovered.
		"""
		for project in self.projects:
			project.du(verbose=verbose)

		# collect stats for shared vs unique frames
		self.calculate_sizes(verbose=verbose)

		print "\n\nTotal FrameMap size:",numberutil.humanize(self.bytes_total,scale='bytes')
		print "Total Shared FrameMap size:",numberutil.humanize(self.bytes_shared,scale='bytes')
		print "Total Self FrameMap size:",numberutil.humanize(self.bytes_self,scale='bytes')
		print "\n\n"

		if verbose:
			for project in self.projects:
				print "Project:",project.full_project_name
				print "  bytes total:",numberutil.humanize(project.bytes_total,scale='bytes')
				print "  bytes shared:",numberutil.humanize(project.bytes_shared,scale='bytes')
				print "  bytes self:",numberutil.humanize(project.bytes_self,scale='bytes')
				print "  frames self:",project.frame_count_self
				print "  frames shared:",project.frame_count_shared
				print "  frames total:",len(project.frames)

		# store the results in the db
		#self.store_results()

	def get_frame_stats(self):
		"""
		Get frame stats from doing a
		series of long listings in the 
		media cache directory
		"""
		path = self.Framestore.path
		print "PATH:",path
#		for _dir in glob.glob("%s/*" % path):
#			for frame in commands.getoutput('ls -lf %s' % _dir):
#				print ">",frame
			
		pass

	def get_frame_stats_threaded(self,threads=12):
		"""
		Get the framestats using the 
		StatThread to speed things up.
		"""
		self.queue = Queue.Queue()
		# spawn the threads
		for i in range(threads):
			print "Starting thread",i
			t = StatThread(self.queue)
			t.setDaemon(True)
			t.start()

		# get frame stats and calculate 
		# the master framesize
		for frame in self.frames.values():
			self.queue.put(frame)

		ttl = self.queue.qsize()
		while not self.queue.empty():
			crnt = ttl - self.queue.qsize()
			pct = int(round(crnt/float(ttl)*100))
			print "  %d of %d [%d%%]\r" % (crnt,ttl,pct),
			sys.stdout.flush()

		print "Queue is empty"
#		self.queue.join()

#		i = 1
#		count = len(self.frames.values())
#		for frame in self.frames.values():
#			frame.framestat()
#			pct = int(round(i/float(count)*100))
#			if verbose:
#				print "  %d of %d [%d%%]\r" % (i,count,pct),
#				sys.stdout.flush()
#			self.bytes_total+=frame.st_size
#			i+=1

	def calculate_sizes(self,verbose=False):
		"""
		Add up all of the frame sizes
		for each project stored in self.projects
		separated by shared vs unique.
		"""
		start = time.time()
		print "  Getting frame sizes..."
		#self.get_frame_stats()
		#print "DONE: Elapsed time:",time.time() - start

		print "\n  Calculating project sizes..."
		for frame in self.frames.values():
			if frame.refcount > 1:
				self.bytes_shared+=frame.st_size
				# get the master(s) for the projects
				# this frame is referenced to.
				# if this frame goes cross-project it 
				# will have more than one master.
				# if there is no master for a project
				# then the project is it's own master
				masters = []
				for project in frame.projects:
					master = self.find_master(project)
					if master not in masters:
						masters.append(master)
				for master in masters:
					master.frame_count_shared+=1
					master.bytes_shared+=frame.st_size
			else:
				self.bytes_self+=frame.st_size
				project = frame.projects[0]
				project.frame_count_self+=1
				project.bytes_self+=frame.st_size
			# add this frame size to the running project
			# total for each project
			for project in frame.projects:
				project.bytes_total+=frame.st_size
		return

	def find_master(self,mapped_project):
	 	"""
		Find the master for the given MappedProject object.
		"""
		if mapped_project.master:
			return mapped_project
		for master in [p for p in self.projects if p.master]:
			if master.key == mapped_project.key:
				return master
		
class MappedProject:
	"""
	A project inside a FrameMap.
	Holds mapped frames associated with the project.
	"""

	def __init__(self,project,Framestore,FrameMap):
		self.full_project_name = project
		self.Framestore = Framestore
		self.FrameMap = FrameMap
		self.frames = {}
		self.master = False
		self.parse_project(project)
		self.frame_count_self = 0
		self.frame_count_shared = 0
		self.bytes_self = 0
		self.bytes_shared = 0
		self.bytes_total = 0

	def parse_project(self,project):
		"""
		Split up the project into it's 
		3 parts: job_number, project_name, extension
		The 'job_key' is the job_number and project_name 
		(no extension).  This is also the project 'group' 
		that subprojects (user projects) fall into.
		"""
		# the regx we're going to use to identify
		# project names. I could pull the name out
		# of the dl_projects table but this grouping
		# is somewhat arbitrary and if someone happens
		# to create a project name manually I want to 
		# catch it. (I also avoid import issues with
		# the dlProject class since it is already 
		# importing the framestore class)
		regx = re.compile('.*([0-9]{2}[A-Z][0-9]{3})[-_]*(.*)(_[A-Z,a-z]*)$')
		try:
			job_num,name,ext = regx.search(project).groups()
			project_key = "%s-%s" % (job_num,name)
		except:
			job_num,name,ext = ('misc',project,None)
			project_key = "misc"
		# set the 'master' flag if this project is a master
		if project[-7:] == '_MASTER':
			self.master = True
		self.job_number = job_num
		self.project_name = name
		self.extension = ext
		self.key = project_key

	def du(self,verbose=False):
		"""
		Collect the unique frames from a project 
		then calculate the size
		NOTE: ** experimental **
			Not sure how accurate the size estimate will be since it's 
			difficult to tell if the API is giving us all the frames
		"""
		dl_project = self.full_project_name
		if verbose: print "[41mP[m %s" % dl_project
		libraries = self.Framestore.get_libraries(dl_project)
		for i,lib in libraries.iteritems():
			if verbose: print "  [42mL[m Getting clips for: %s" % lib['name']
			for clip in self.Framestore.get_clips(lib['node']):
				frame_count = self.Framestore._get_frame_count(clip['node'])
				# NOTE: pulling the metadata for still frames seems 
				# to crash the wiretapd so we'll skip them for now. 
				if frame_count < 2:
					continue
				if verbose:
					print "    [44mC[m Getting %s frames for: %s" % (frame_count.__int__(),clip['name'])
				try:
					_frames = self.Framestore.get_frames(clip['node'],stream='DMXEDL')
					#_frames = self.Framestore.get_frames(clip['node'],stream='XML')
				except Exception,error:
					# clips in Lost_+_Found are apparently
					# not wiretap friendly
					if lib['name'] != 'Lost_+_Found':
						print "get_frames failed for %s" % clip['name']
						for k,v in clip.iteritems():
							print "\t%s: %s" % (k,v)
						print "Error:",str(error)
				except KeyboardInterrupt:
					raise
				else:
					for frame in _frames:
						self.add_frame(frame)

	def add_frame(self,frame):
		"""
		Add a frame to this mapped project
		and also to the master frame list
		"""
		# if this frame is not already in the master
		# frame map, add it.
		if not self.FrameMap.frames.has_key(frame):
			self.FrameMap.frames[frame] = MappedFrame(frame,self)
		else:
			# if the frame is already in the master map
			# then add this project to the MappedFrame
			self.FrameMap.frames[frame].add_project(self)
		# store the MappedFrame in this MappedProject as well
		if not self.frames.has_key(frame):
			frame_obj = self.FrameMap.frames[frame]
			self.frames[frame] = frame_obj
			if len(frame_obj.projects) == 1:
				self.frame_count_self+=1
			elif len(frame_obj.projects) > 1:
				self.frame_count_shared+=1


class MappedFrame:
	"""
	A frame inside of a FrameMap.
	Stores information about an idividual
	frame in the media cache like size
	and # of hardlinks etc...
	"""

	def __init__(self,path,MappedProject):
		self.path = path
		self.st_size = 0
		self.nlink = 0
		self.projects = [MappedProject]
	
	def __getattr__(self,name):
		if name == 'refcount':
			return len(self.projects)
		message = "'%s' has no attribute %s" % (__name__,name)
		raise AttributeError,message
	
	def add_project(self,MappedProject):
		"""
		Adds a project to the list
		of projects that reference 
		this frame.
		"""
		if MappedProject.full_project_name not in [n.full_project_name for n in self.projects]:
			self.projects.append(MappedProject)
	
	def framestat(self,verbose=False):
		"""
		Get frame stats
		"""
		if verbose: print "\t\t\t[43mF[m %s\r" % self.path,
		try:
			stat = fileutil.stat(self.path)
			self.st_size = stat.st_size
			self.st_nlink = stat.st_nlink
		except:
			if verbose: print "\t\t\t[41mERROR[m: could not get size for %s" % self.path
		if verbose:print



if __name__ == '__main__':
	#f = Framestore.find(host='flame03',volume='stonefs4')[0]
	#fs = Framestore.find(status='active')

	fs = Framestore('flame01',4)
#	print fs.get_projects()

	fs.du(verbose=True)

#	fs.du(source='db',verbose=True)


#	print fs.pstats
#	a = fs.scan_libraries()
#	s4 = fs.get_projects()
#	print "\nSTONEFS5"
#	for i,p in s4.iteritems():
#		print "\t",p



#	f = Framestore.find(uid=10)[0]
#	fs = Framestore.find(status='active')
#	for f in fs:
#		f.sync_libraries()
#		f.show_locks()


	pass
