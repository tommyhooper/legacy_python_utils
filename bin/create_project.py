#!/usr/bin/python

#import MySQLdb,MySQLdb.cursors
import time,datetime,sys,string,re,os
sys.path.append('/Volumes/discreet/lib/python2.3/site-packages')
import A52
from A52.vTree import vTree

from optparse import OptionParser
p = OptionParser()
p.add_option("-j",dest='job_num', type='string',help="Job number. e.g. 11A123")
p.add_option("-p",dest='project_name', type='string',help="Project name. e.g. Dodge_Fast")
p.add_option("-f",dest='framestore', type='string',help="Framestore. e.g. SANSTONE1")
options,args = p.parse_args()
job_num = options.job_num
project_name = options.project_name
framestore = options.framestore

if not job_num or not project_name or not framestore:
	print ""
	#p.print_usage()
	p.print_help()
	sys.exit()

# validate the job_num
if not re.search('^[0-9]{2}[AERD][0-9]{3}$',job_num):
	print "Job number is invalid. %s" % job_num
	sys.exit()

# clean the project_name
project_name = A52.utils.clean_string(project_name)

# validate the framestore
fs_obj = A52.Framestore.find(name=framestore)
if not fs_obj:
	print "Could not find framestore: %s" % framestore
	print "Should be one of:"
	all_fs = A52.Framestore.find()
	for fs in all_fs:
		print "\t",fs.data['name']
	sys.exit()
framestore = fs_obj[0]

# categorize the job_number for which nas to use
# nas2 is for elastic (E)
# nas0 is for A52 (A)
# nas0 is for RPS (R) (and everything else for now)
if job_num[2] == 'A':
	nas = 'nas0'
	main_dir = 'CGI'
elif job_num[2] == 'E':
	nas = 'nas2'
	main_dir = 'ELASTIC'
elif job_num[2] == 'R':
	nas = 'nas0'
	main_dir = 'CGI'

# create the project in the db
user = os.getenv('USER')
project = A52.Project.create(job_num,project_name,user,discreet_viewable=1,status='active')[0]
proj_full_name = "%s_%s" % (project.data['job_num'],project.data['name'])
print "PROJECT:",project


# create the project directories
#dest_path = "/disks/%s/%s" % (nas,main_dir)
#tree = vTree.load('cg','project')
#tree.Create(dest_path,project=proj_full_name)
#tree.show()



