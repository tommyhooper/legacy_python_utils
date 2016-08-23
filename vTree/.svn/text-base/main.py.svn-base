#!/usr/bin/python

import os,stat,pwd,grp,re
from A52 import utils
from models import Tree
from models import Directory
from models import File

class vTree(Tree):
	"""
	Virtual Directory Tree. 

	Represents a directory tree as a Dictionary.

	{
	HOME_DIRECTORY:	{
				Subdirectory:	{
							Subdirectory: {},
							Subdirectory: {}
							},
				Subdirectory:	{
							Subdirectory: {}
							}
				}
	}

	variables can be substituted within the tree by using the
	format __<VARIABLE NAME>__
	i.e. __PROJECT__ --> verizon
	"""
	def __init__(self):
		"""
		vTree object
		"""
		self.vTree = {}
		self.obj_map = {}
		self.dirs = []
		self.files = []
		self.data = {	'uid':None,
					'department':None,
					'tree_type':None,
					'name':None
					}
		# init the browser values
		self.cwd = {'/':{}}


	def _add_path(self,path):
		"""
		Add a directory to the vTree
		"""
		tree = self.vTree
		dirs = path.split('/')
		for i in range(0,len(dirs),1):
			if dirs[i]:
				if not tree.has_key(dirs[i]):
					try: 
						tree[dirs[i]] = {}
					except: 
						tree[dirs[i]] = {dirs[i+1]:{}}
				tree = tree[dirs[i]]

	def _remove_path(self,path):
		"""
		Remove a directory from the vTree
		"""
		# iterate through the object map and 
		# remove anything that matches our path
		for obj_path in self.obj_map:
			if obj_path.find(path) >= 0:
				self.dirs.remove(self.obj_map[obj_path])
		self._build_vTree()

	def _build_vTree(self,**kwargs):
		"""
		Construct the vTree in a Dictionary 
		"""
		# clear the tree first
		self.vTree = {}
		for group in [self.dirs,self.files]:
			for obj in group:
				if kwargs:
					obj.rep_path = self._replace(obj.data['path'],**kwargs)
				else:
					obj.rep_path = obj.data['path']
				self._add_path(obj.rep_path)
				self.obj_map[obj.data['path']] = obj
		# set the cwd to the top level of the vTree
		self.set_cwd("/")

	def _replace(self,path,**kwargs):
		"""
		Replace all keywords in the given path
		kwargs are lowercase replacement definitions for
		the __<NAME>__ directories in the tree... e.g.:
			to replace __PROJECT__ directories specify:
			project='some project name'
		"""
		# loop through each directory path, replacing whatever
		# keywords we find 
		rep_list = re.findall('__[A-Z]*__',path)
		if rep_list:
			used_keys,unused_keys = [[],[]]
			for rep in rep_list:
				keyword = rep.strip('__').lower()
				if not rep in used_keys and kwargs.has_key(keyword):
					path = path.replace(rep,kwargs[keyword])
					used_keys.append(rep)
				else:
					unused_keys.append(rep)
		for key in unused_keys:
			print "[41mWARNING:[m Unused replacement key: %s" % key 
		return path

	# staticmethod
	def clear(self):
		"""
		Clear the object. Just run the __init__
		"""
		self.__init__()

	def show(self,**kwargs):
		"""
		Print a user sensable view of the vTree
		"""
		self._build_vTree(**kwargs)
		utils.print_array(self.vTree)

	def show_map(self):
		"""
		Print a user sensable view of the object map
		"""
		if not self.vTree:
			self._build_vTree()
		utils.print_array(self.obj_map)


	def walk(self,path,include_files=True):
		"""
		Walk 'path' and map the directories into the main vTree
		"""
		# add the last directory in the 'path' as our top level
		# directory in the vTree
		base_path = os.path.dirname(path)
		root_dir= os.path.basename(path)
		os.chdir(base_path)
		if os.path.isdir(root_dir):
			self.dirs.append(Directory(path=root_dir))
		else:
			print "Error: Could not find %s" % path
			return
		for root, dirs, files in os.walk(root_dir):
			for directory in dirs:
				self.dirs.append(Directory(path="%s/%s" % (root,directory)))
			if include_files:
				for fl in files:
					self.files.append(File(path="%s/%s" % (root,fl)))

	def add_directory(self,path):
		"""
		Add a directory to the vTree
		"""
		self._add_path(path)

	def remove_directory(self,path,recursive=False):
		"""
		Remove a directory from the vTree
		"""
		# if recursive is false check to make sure
		# the path does not have children
		cwd = self.set_cwd(path)
		if not recursive and cwd.values():
			print "Error removing %s: Directory not empty" % (path)
			return
		self._remove_path(path)

	def ls(self):
		"""
		vTree.ls
		"""
		path = self.cwd.keys()[0]
		for item in self.cwd.values()[0]:
			obj = self.obj_map["%s/%s" % (path,item)]
			mode = self.convert_st_mode(obj.data['st_mode'])
			user = pwd.getpwuid(obj.data['st_uid'])[0]
			group = grp.getgrgid(obj.data['st_gid'])[0]
			line = "%5s %5s %5s  %s" % (mode,user,group,item)
			print line

	def convert_st_mode(self,st_mode,to='human'):
		"""
		Convert st_mode into 'rwx' format
		to = 'human','octal'
		#mode = stat.S_IMODE(st_mode) & 0777
		"""
		if to == 'octal':
			return oct(stat.S_IMODE(st_mode))
		# 'human' readable mode
		_tt = '-'
		_ur,_uw,_ux = ['-','-','-']
		_gr,_gw,_gx = ['-','-','-']
		_or,_ow,_ox = ['-','-','-']
		# File / Directory
		if st_mode & stat.S_IFDIR:
			_tt = 'd'
		# USER
		if st_mode & stat.S_IRUSR:
			_ur = 'r'
		if st_mode & stat.S_IWUSR:
			_uw = 'w'
		if st_mode & stat.S_IXUSR:
			_ux = 'x'
		# GROUP
		if st_mode & stat.S_IRGRP:
			_gr = 'r'
		if st_mode & stat.S_IWGRP:
			_gw = 'w'
		if st_mode & stat.S_IXGRP:
			_gx = 'x'
		# OTHERS
		if st_mode & stat.S_IROTH:
			_or = 'r'
		if st_mode & stat.S_IWOTH:
			_ow = 'w'
		if st_mode & stat.S_IXOTH:
			_ox = 'x'
		human_mode = "%s%s%s%s%s%s%s%s%s%s" % (_tt,_ur,_uw,_ux,_gr,_gw,_gx,_or,_ow,_ox)
		return human_mode


	def set_cwd(self,path):
		"""
		Set the current directory to 'path'
		"""
		if not self.vTree: self._build_vTree()
		# force our path to be absolute
		path = "/%s" % (path.strip("/"))
		# take our path and walk it (virtually)
		base_dirs = []
		below = self.vTree
		for i in range(0,len(path.split("/")),1):
			path_iter = path.split("/")[i]
			if path_iter:
				if below.has_key(path_iter):
					base_dirs.append(path_iter)
					below = below[path_iter]
				else:
					# no such file or directory
					print "Error: No such file or directory: %s" % path_iter
					return 
		base_path = "/%s" % ("/".join(base_dirs))
		self.cwd = {base_path:below}
		return self.cwd



	def Save(self,department=None,tree_type=None,name=None):
		"""
		Save the vTree in the db
		"""
		if department:
			self.data['department'] = department
		if tree_type:
			self.data['tree_type'] = tree_type
		if name:
			self.data['name'] = name

		error = []
		if not self.data['department']:
			error.append("Missing department.")
		if not self.data['tree_type']:
			error.append("Missing vTree type.")
		if error:
			print "Error saving vTree:"
			for message in error:
				print "\t",message
			return

		# find the version number and increment it
		existing = Tree.find(	department=self.data['department'],
						tree_type=self.data['tree_type'],
						name=self.data['name'])
		if existing:
			self.data['version'] = float(existing[0].data['version']) + .1
		else:
			self.data['version'] = 1.0
		# save the main vtree
		self.save()
		# save the directories
		for dir_obj in self.dirs:
			dir_obj.data['vTree_uid'] = self.data['uid']
			dir_obj.save()
		# save the files
		for file_obj in self.files:
			file_obj.data['vTree_uid'] = self.data['uid']
			# have the file object get the conetents of the file
			file_obj.read()
			file_obj.save()
	
	def Create(self,base_dir,**kwargs):
		"""
		Create the directory tree under 'base_dir'
		kwargs are lowercase replacement definitions for
		the __<NAME>__ directories in the tree... e.g.:
			to replace __PROJECT__ directories specify:
			project='some project name'
		"""
		if not os.path.exists(base_dir):
			message = "Path not found: %s" % base_dir
			raise Exception,message
			#return (False,message)
		if not os.access(base_dir,os.W_OK):
			message = "Cannot write to %s" % base_dir
			raise Exception,message
			#return (False,message)

		# group the paths we need to make by level
		levels = {}
		for dir_obj in self.dirs:
			rep_path = self._replace(dir_obj.data['path'],**kwargs)
			count = rep_path.count('/')
			if not levels.has_key(count):
				levels[count] = {}
			if not levels[count].has_key(rep_path):
				levels[count][rep_path] = dir_obj
	
		# iterate through each level and make the paths
		chmod_warn = False
		chown_warn = False
		exit_msg = ''
		for lvl in levels:
			for rel_path,obj in levels[lvl].items():
				st_mode = obj.data['st_mode']
				st_uid = obj.data['st_uid']
				st_gid = obj.data['st_gid']
				full_path = "%s/%s" % (base_dir,rel_path)
				if not os.path.exists(full_path):
					os.mkdir(full_path)
					# change the owners and the permissions
					# this could fail if we do not have permission
					# so print a warning and continue so it can be 
					# fixed externally
					try: os.chmod(full_path,st_mode)
					except: chmod_warn = True
					try: os.chown(full_path,st_uid,st_gid)
					except: chown_warn = True
		if chmod_warn:
			_msg = "WARNING: Could not change permission on some directories."
			#print _msg
			exit_msg += "%s\n" % _msg
		if chown_warn:
			_msg = "WARNING: Could not change owner of some directories."
			#print _msg
			exit_msg += "%s\n" % _msg
		return (True,exit_msg)

	def Delete(self):
		"""
		Delete an existing vTree
		"""
		if not self.data['uid']:
			print "vTree has not been saved (nothing to delete)"
			return
		# first we have to delete all the related
		# directories and files for this vTree
		for dir_obj in self.dirs:
			dir_obj.delete()
		for file_obj in self.files:
			file_obj.delete()
		# finally delete the main vTree
		self.delete()

	# staticmethod
	def load(department,tree_type,version=None,name=None,verbose=False):
		"""
		Load a vTree from the db
		"""
		tree = vTree.find(department=department,tree_type=tree_type,name=name,version=version,limit='last')
		if not tree: return None
		tree = tree[0]
		if verbose:
			print "\nLoaded vTree:"
			print "  %-12s %s"  % ('Name:',tree.data['name'])
			print "  %-12s %s" % ('Department:',tree.data['department'])
			print "  %-12s %s" % ('Tree Type:',tree.data['tree_type'])
			print "  %-12s %s\n" % ('Version:',tree.data['version'])
		tree.dirs = Directory.find(vTree_uid=tree.data['uid'])
		tree.files = File.find(vTree_uid=tree.data['uid'])
		return tree


# static / cass method declarations
	load = staticmethod(load)
if __name__ == '__main__':
#	t = vTree.load('cg','project')
#	t.show()
#	t.Forge('/tmp/',project='Verizon',spot='fios30',user='tommy')
	
#	t = vTree.load('cg','shot')
#	t.Forge('/tmp/',project='Verizon',spot='fios30',user='tommy',shot='fx01')
#	t.show()

#	t = vTree.load('cg','shot')
#	t.Create('/home/tmy/tmp/',project='Verizon',spot='fios30',user='tommy',shot='fx01')
#	t.show()

#	p = vTree()
#	p.walk('/home/tmy/src/A52/vTree/samples/CGI/__PROJECT__',include_files=True)
#	p.Save(department='cg',tree_type='project')

#	s = vTree()
#	s.walk('/Volumes/discreet/dev/python2.3/site-packages/A52/vTree/__SPOT__',include_files=False)
#	s.show()
#	s.Save(department='cg',tree_type='spot')
	
	s = vTree()
	s.walk('/Volumes/discreet/dev/python2.3/site-packages/A52/vTree/templates/__PROJECT__',include_files=False)
	s.show()
#	s.Save(department='cg',tree_type='spot')
	s.Save(department='design',tree_type='spot')
	pass



