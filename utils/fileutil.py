import os
import stat
import sys
import types
import re
import datetime
import traceback
import glob
import dateutil


def list_dirs(path, exclude_extensions=[], only_extensions=[], exclude_files=[], only_files=[]):
    """ 
    Recurse through a directory returning all files or all files that match the passed filters.
    For example specifying only_files will return only files that have the matching name.
    Similarly, if you specify an exclude list then the method will not return files or extensions listed in 
    the exclude list
    """
    file_list = []
    for root, sub_folders, files in os.walk(path):
        for file in files:
            base, ext = os.path.splitext(file)
            include_file = False
            
            if len(exclude_files) or len(exclude_extensions):
                include_file = True
                if len(only_files) or len(only_extensions):
                    include_file = False
                
            if file in exclude_files:
                include_file = False
            if file in only_files:
                include_file = True
            if ext in exclude_extensions:
                include_file = False
            if ext in only_extensions:
                include_file = True
   
            if include_file:
                 file_list.append(os.path.join(root, file))
                 
    return file_list

def makedirs(name,perm=02777,uid=0,gid=0):
	"""
	Create a directory (or directories recursively)
	and set the correct permissions.
	"""
	if type(uid) == types.StringType: uid = pwd.getpwnam(uid)[3]
	if type(gid) == types.StringType: gid = grp.getgrnam(gid)[2]
	_makedirs(name,perm=perm,uid=uid,gid=gid)

def _makedirs(name,perm=02777,uid=0,gid=0):
	"""_makedirs(path [, perm=02775] [,uid=33] ,[gid=33])
	_makedirs but sets the proper permissions.
	*IMPORTANT: uid and gid must be int's
	"""
	head, tail = os.path.split(name)
	if not tail:
		head, tail = os.path.split(head)
	if head and tail and not os.path.exists(head):
		_makedirs(head, perm, uid, gid)
	if not os.path.exists(name):
		os.mkdir(name)
		if uid and gid:
			os.chown(name, uid, gid)
		elif uid:
			os.chown(name, uid, os.getgid())
		elif gid:
			os.chown(name, os.getuid(), gid)
		os.chmod(name,perm)

def symlink(target,link,sudo=False,archive_tag='ori'):
	"""
	Checks for the existence of a link before making  or remaking it.
	If 'link' exists and is a link, the link is remade.
	If 'link' target exists and is either a file or directory we do nothing.
	"""
	if exists(link):
		if islink(link):
			# link exists and is actually a link - remove it
			try:
				if sudo:
					os.system('sudo rm %s' % (link))
				else:
					os.remove(link)
			except:
				# remove failed
				traceback.print_exc(file=sys.stdout)
				return False
		else:
			# 'link' exists and is not a link, move whatever it is aside
			if not archive(link,archive_tag=archive_tag):
				print "Archive of %s failed... not creating link" % link
				return False
	# should be clear to make the link from here
	try:
		if sudo:
			#print "SUDO LINK: %s --> %s" % (target,link)
			os.system('sudo ln -s %s %s' % (target,link))
		else:
			#print "LINK: %s --> %s" % (target,link)
			os.symlink(target,link)
	except Exception,message:
		# create failed
		traceback.print_exc(file=sys.stdout)
		return False

def exists(name):
	"""
	Tests if 'name' exists by using lstat
	so that symbolic links are not followed.
	(os.path.exists on a bad link returns False)
	"""
	try:
		lstat = os.lstat(name)
	except:
		return False
	return True

def isdir(name):
	"""
	Tests if 'name' is a directory using lstat
	so that symbolic links are not followed.
	"""
	lstat = os.lstat(name)
	return stat.S_ISDIR(lstat.st_mode)

def islink(name):
	"""
	Tests if 'name' is a link using lstat
	in order to test the link and not the
	referant.
	"""
	import stat
	lstat = os.lstat(name)
	return stat.S_ISLNK(lstat.st_mode)

def isfile(name):
	"""
	Tests if 'name' is a regular fil using lstat
	so that symbolic links are not followed.
	"""
	lstat = os.lstat(name)
	return stat.S_ISREG(lstat.st_mode)

def archive(name,archive_tag='ori'):
	"""
	Move a directory aside by appending
	a .ori to the name (or ori2,3,4 etc...)
	"""
	if not os.path.exists(name):
		print "Archive: %s not found." % name
		# still return true since the main point
		# is to make sure 'name' doesn't get overwritten
		return True
	dest = "%s.%s" % (name,archive_tag)
	ori_count = len(glob.glob("%s*" % dest))
	if ori_count > 0:
		dest = "%s.%s" % (name,dateutil.legible_date(format_id=21))
	try:
		os.rename(name,dest)
	except:
		traceback.print_exc(file=sys.stdout)
		return False
	return True

def st_size(filename):
	_stat = os.lstat(filename)
	st_size = _stat.st_size
	if type(st_size) is int:
		return st_size
	else:
		message = "Could not get filesize for %s" % filename
		raise Exception,message

def mod_date(filename):
	_stat = os.lstat(filename)
	try:
		return dateutil.timestamp_to_datetime(_stat.st_mtime,result='object')
	except:
		message = "Could not get modification time for %s" % filename
		raise Exception,message

def stat(filename):
	return os.lstat(filename)

if __name__ == '__main__':
	#archive('directory')
	symlink('target','new_link')
	#symlink('/home/tmy/src/stat_test/file','/home/tmy/src/stat_test/immovable')
	pass



