

from models import spots
from A52.db import controller
from A52.utils import print_array
from A52.Project import Project
from A52.vTree import vTree
db = controller()

import logging
log = logging.getLogger(__name__)

import datetime


class Spot(spots):


	def __init__(self,**kwargs):
		"""
		Spot Object
		"""
		self.data = {}
		self.data.update(kwargs)

	def create_vTree(self):
		"""
		Create the vTree for this spot
		"""
		# we need the project object
		proj = Project.find(uid=self.data['project_uid'])[0]
		log.info("Creating vTree")
		if proj.data['job_num'][2] == 'A':
			nas = 'nas0'
			main_dir = 'CGI'
			print("vTree.load('cg','spot')")
			tree = vTree.load('cg','spot')
		elif proj.data['job_num'][2] == 'E':
			nas = 'nas2'
			main_dir = 'ELASTIC'
			print("vTree.load('design','spot')")
			tree = vTree.load('design','spot')
		elif proj.data['job_num'][2] == 'R':
			nas = 'nas0'
			main_dir = 'CGI'
			print("vTree.load('cg','spot')")
			tree = vTree.load('cg','spot')
		print "TREE:",tree
		# create the project directories
		log.info("tree: %s" % tree)
		cg_project_name = "%s_%s" % (proj.data['job_num'],proj.data['name'].lower())
		dest_path = "/disks/%s/%s/%s/shot" % (nas,main_dir,cg_project_name)
		log.info("\nCreating spot tree on %s" % (dest_path))
		return tree.Create(dest_path,spot=self.data['name'])


if __name__ == '__main__':
#	s = Spot.find(uid=11)[0]
#	s.create_vTree()
	tree = vTree.load('cg','spot')
	print "TREE:",tree
#	from datetime import datetime
#	s = Spot(	name = 'spot_one',
#			project_uid = 11,
#			producer = 'megan',
#			status = 'active',
#			start_date = datetime.today())
#	if not s.create():
#		print "Failed"
#	print s
	pass
