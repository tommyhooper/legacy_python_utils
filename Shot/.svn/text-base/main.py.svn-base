

from models import shots
from A52.db import controller
from A52.utils import print_array
from A52.Project import Project
from A52.Spot import Spot
from A52.vTree import vTree
db = controller()

import datetime


class Shot(shots):


	def __init__(self,**kwargs):
		"""
		Spot Object
		"""
		self.data = {}
		self.data.update(kwargs)

	def create_vTree(self,user_id=None):
		"""
		Create the vTree for this shot.
		If a user_id is specified only
		create that user's user directories,
		otherwise create all user directories
		for users assigned to that shot.
		"""
		# we need the project object
		proj = Project.find(uid=self.data['project_uid'])[0]
		# we need the spot object
		spot = Spot.find(uid=self.data['spot_uid'])[0]
		#log.info("Creating vTree")
		if proj.data['job_num'][2] == 'A':
			nas = 'nas0'
			main_dir = 'CGI'
			tree = vTree.load('cg','shot')
			user_tree = vTree.load('cg','user')
		elif proj.data['job_num'][2] == 'E':
			nas = 'nas2'
			main_dir = 'ELASTIC'
			tree = vTree.load('design','shot')
			user_tree = vTree.load('design','user')
		elif proj.data['job_num'][2] == 'R':
			nas = 'nas0'
			main_dir = 'CGI'
			tree = vTree.load('cg','shot')
			user_tree = vTree.load('cg','user')
		# create the project directories
		cg_project_name = "%s_%s" % (proj.data['job_num'],proj.data['name'].lower())
		dest_path = "/disks/%s/%s/%s/shot/%s" % (nas,main_dir,cg_project_name,spot.data['name'])
		print "Creating shot tree on %s" % (dest_path)
		tree.Create(dest_path,shot=self.data['name'])

		shot_path = "%s/%s" % (dest_path,self.data['name'])
		# create user directories inside the shot tree
		for res in proj.get_resources('artist'):
			if user_id and res.data['resource_id'] != user_id:
				# if user_id is set and it doesn't match
				# this resource - skip 
				pass
			else:
				print "Creating user directory: %s" % res.data['resource_id']
				user_tree.Create(shot_path,user=res.data['resource_id'])


if __name__ == '__main__':
	s = Shot.find(uid=8)[0]
	s.create_vTree(user_id='chrisj')
	pass
