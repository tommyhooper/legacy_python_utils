#!/usr/bin/env python

import os,glob,sys
from A52.Project import Project

class Setups:
	def __init__(self,job_num):
		"""
		Setup the object based on a single
		discreet project directory tree:
		'project_home'
		"""
		self.job_num = job_num
		self.hosts = ['flame1','flame2','flame3','flame4','flare1','smoke2','smack1']
		self.local_projects = []
		self.central_project = self.find_central_project()

	def find_local_projects(self):
		"""
		Search the flames / flares / smokes 
		for local versions of this project
		"""
		for host in self.hosts:
			dl_glob = "/hosts/%s/usr/discreet/project/?*%s*" % (host,self.job_num)
			projects = glob.glob(dl_glob)
			for project in projects:
#				print ">",project
				self.local_projects.append(project)

	def find_central_project(self):
		"""
		Find the central project
		"""
		dl_glob = "/disks/nas2/discreet/project/*%s*" % self.job_num
		search = glob.glob(dl_glob)
		if len(search) == 1:
			return search[0]
		elif len(search) > 1:
			print "Error: more than one project found..."
			for project in search:
				print "\t",project
			return None
		else:
			print "Error: central project not found for %s" % self.job_num
			return None


	def migrate(self):
		"""
		Sync setups from the local projects to
		the central project
		"""
		if not self.central_project:
			print "Error: no central project"
			return
		for proj in self.local_projects:
			command = "rsync -av %s/ %s" % (proj,self.central_project)
			print ">>",command
			os.system(command)

	def get_project_name(self):
		p = A52.Project.find(job_num=self.job_num)[0]
		self.dl_project_basename = "%s-%s" % (p.data['job_num'],p.data['name'])
		print "NAME:",self.dl_project_basename

	def create_project_directories(self):
		project_dir = "/disks/nas2/discreet/project/%s" % (self.dl_project_basename)
		# rsync the template to the main project location
		command = "rsync -a /disks/nas2/discreet/templates/2011/project/flame/ %s/" % (project_dir)
		print "Syncing project template: %s" % command
 		success = os.system(command)

if __name__ == '__main__':
	#11A110
#	s = Setups('11A110')
#	s.find_local_projects()
#	s.migrate()
#	jobs = ['11A144', '11A140','11A121', '10E117', '09A195', '11A124']
#	nc_jobs = ['11A139','11A134','10A210','10E196','10E204','11E506']

	nc_jobs = ['11A107','11A128','11A115','11A126','11A127','11A141']
	for job in nc_jobs:
		s = Setups(job)
		s.find_central_project()
		s.find_local_projects()
		s.migrate()





