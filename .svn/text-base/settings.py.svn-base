"""
connection_name: map pointing actual database settings
"""
ripley = '192.168.98.56'
ripley = 'ripley'
bishop = 'bishop'
localhost = '127.0.0.1'
live_db_server = 'bishop'
dev_db_server = bishop

import os
cwd = os.path.dirname(os.path.abspath(__file__))
resource_dir = os.path.dirname(cwd)

DB_PROPERTIES = {}
DB_PROPERTIES['dev'] = {	'a52_production': {	'db':'a52_production',
									'username':'pyre',
									'password':'',
									'host':dev_db_server},
					'a52_discreet': {	'db':'a52_discreet',
								'username':'pyre',
								'password':'',
								'host':dev_db_server},
					'atempo': {	'db':'atempo',
								'username':'pyre',
								'password':'',
								'host':dev_db_server}}
DB_PROPERTIES['live'] = {	'a52_production': {	'db':'a52_production',
									'username':'pyre',
									'password':'',
									'host':live_db_server},
					'a52_discreet': {	'db':'a52_discreet',
								'username':'pyre',
								'password':'',
								'host':live_db_server},
					'atempo': {	'db':'atempo',
								'username':'pyre',
								'password':'',
								'host':live_db_server}}

DL_PROPERTIES = {}
DL_PROPERTIES['live'] = {	'resource_dir':'/Volumes/discreet/lib/python2.3/site-packages',
					'template_dir':'/Volumes/discreet/templates',
					'user_setup_home':'/Volumes/discreet/user',
					'project_setup_home':'/Volumes/discreet/project',
					'dl_base':'/Volumes/discreet',
					'dl_share':'/Volumes/discreet',
					'cfg_file':'1920x1080@23976psf.cfg',
					'init_file':'init.cfg',
					'engineering_user_id':'beam',
					'project_resolution_name':'HD 1080',
					'dl_libraries':['IN','OUT','VFX','ELEMENTS','CONFORMS','EDITS','POST','Default'],
					'dl_master_libraries':['MASTER','IN','OUT','VFX','ELEMENTS','CONFORMS','EDITS','POST','Default']
					}
DL_PROPERTIES['dev'] = {	'resource_dir':resource_dir,
					'template_dir':'/Volumes/discreet/templates',
					'user_setup_home':'/Volumes/discreet/user',
					'project_setup_home':'/Volumes/discreet/project',
					'dl_base':'/Volumes/discreet',
					'dl_share':'/Volumes/discreet',
					'cfg_file':'1920x1080@23976psf.cfg',
					'init_file':'init.cfg',
					'engineering_user_id':'beam',
					'project_resolution_name':'HD 1080',
					'dl_libraries':['IN','OUT','VFX','ELEMENTS','CONFORMS','EDITS','POST','Default'],
					'dl_master_libraries':['MASTER','IN','OUT','VFX','ELEMENTS','CONFORMS','EDITS','POST','Default']
					}



