

from A52.utils import print_array
from A52.Interdubs import Interdubs
from A52.vTree import vTree
from A52.Atempo import DiscreetArchive

from datetime import *
import time
import logging
log = logging.getLogger(__name__)

class Project:


	def __init__(self,**kwargs):
		pass

	#@staticmethod 
	def create_vTree(self,project_name):
		"""
		Create the vTree for this project
		"""
		log.info("Creating vTree")
		job_num,name = Project.parse_project_name(project_name)
		if job_num[2] == 'A':
			nas = 'nas0'
			main_dir = 'CGI'
			tree = vTree.load('cg','project')
		elif job_num[2] == 'E':
			nas = 'nas2'
			main_dir = 'ELASTIC'
			tree = vTree.load('design','project')
		elif job_num[2] == 'R':
			nas = 'nas0'
			main_dir = 'CGI'
			tree = vTree.load('cg','project')
		# create the project directories
		dest_path = "/disks/%s/%s" % (nas,main_dir)
		cg_project_name = "%s_%s" % (self.data['job_num'],self.data['name'].lower())
		#print "\nCreating %s tree on %s" % (main_dir,dest_path)
		return tree.Create(dest_path,project=cg_project_name)
	create_vTree = staticmethod(create_vTree)

	#@staticmethod
	def create_interdubs_folder(self,project_name):
		"""
		Create the interdubs folder for this project
		"""
		job_num,name = Project.parse_project_name(project_name)
		i = None
		if job_num[2] == 'A':
			i = Interdubs(company='a52')
		elif job_num[2] == 'E':
			i = Interdubs(company='elastic')
		elif self.data['job_num'][2] == 'R':
			pass #i = Interdubs(company='rps')
			message = 'Cannot create RPS Interdubs folders yet.'
			raise Exception,message
		else:
			message = 'Could not determine company from job number: %s' % job_num
			raise Exception,message

		idubs_folder = "%s_%s" % (job_num,name)
		if not i.create_folder(idubs_folder):
			message = "Failed to create Interdubs folder."
			raise Exception,message
		return 
	create_interdubs_folder = staticmethod(create_interdubs_folder)

	#@staticmethod
	def create_dl_archive_folder(self):
		"""
		Create the dl archive folder for this project
		"""
		job_num,name = Project.parse_project_name(project_name)
		arch_name = "%s-%s" % (job_num,name)
		dla = DiscreetArchive(project=arch_name)
		dla.create_project_folder()
		return 
	carete_dl_archive_folder = staticmethod(create_dl_archive_folder)

	#@staticmethod
	def parse_project_name(name):
		"""
		Assuming 'name' is a project name
		with the job number in it, this function
		will attempt to split the components apart.
		"""
		try:
			jnum,pname = re.match('(^[0-9]{2}[AERD][0-9]{3})(.*)',name).groups()
		except:
			return name
		return (jnum,pname.strip())
	parse_project_name = staticmethod(parse_project_name)



if __name__ == '__main__':
	pass



