import sqlalchemy
from sqlalchemy import Table, MetaData, Column, String, Integer, Text, DateTime, Float, SmallInteger
from sqlalchemy.orm import mapper
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()

class resolutions(base):
	#def create_resolutions(database):
	""" resolutions:
	| uid    | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| name   | varchar(48)           | YES  |     | NULL    |                |
	| width  | smallint(5) unsigned  | YES  |     | NULL    |                |
	| height | smallint(5) unsigned  | YES  |     | NULL    |                |
	| aspect | decimal(6,4)          | YES  |     | NULL    |                |
	"""
	__tablename__ = 'resolutions'
	uid = Column(Integer(unsigned=True), primary_key=True, autoincrement=True)
	name = Column(String(48))
	width = Column(SmallInteger)
	height = Column(SmallInteger)
	aspect = Column(Float(precision=4,asdecimal=True))
	
	def __init__(self,database=None):
		engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
		Session = sessionmaker(bind=engine)
		self.session = Session()
	
	def save(self):
		self.session.add(self)
		self.session.commit()
#	def __repr__(self):
#		pass

def create_projects(database):
	""" projects:
	| uid               | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| job_num           | varchar(24)           | YES  |     | NULL    |                |
	| name              | varchar(128)          | YES  |     | NULL    |                |
	| created_by        | varchar(48)           | YES  |     | NULL    |                |
	| producer          | varchar(128)          | YES  |     | NULL    |                |
	| discreet_viewable | tinyint(1) unsigned   | YES  |     | NULL    |                |
	| creation_date     | datetime              | YES  |     | NULL    |                |
	| status            | varchar(24)           | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('projects', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('job_num',String(24)),
		Column('name',String(128)),
		Column('created_by',String(48)),
		Column('producter',String(128)),
		Column('discreet_viewable',SmallInteger),
		Column('creation_date',DateTime),
		Column('status',String(24)))
	metadata.create_all(engine)

def create_vTrees(database):
	""" vTrees:
	| uid         | mediumint(8) unsigned             | NO   | PRI | NULL    | auto_increment |
	| department  | enum('cg','design','compositing') | YES  |     | cg      |                |
	| tree_type   | enum('project','shot')            | YES  |     | NULL    |                |
	| version     | decimal(5,4)                      | YES  |     | NULL    |                |
	| name        | varchar(128)                      | YES  |     | NULL    |                |
	| description | text                              | YES  |     | NULL    |                |
	| date        | datetime                          | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('vTrees', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('department',String(24)),
		Column('tree_type',String(24)),
		Column('version',Float(asdecimal=True)),
		Column('name',String(128)),
		Column('description',Text),
		Column('date',DateTime))
	metadata.create_all(engine)

def create_vTree_directories(database):
	""" vTree_directories:
	| uid       | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| vTree_uid | mediumint(8) unsigned | YES  |     | NULL    |                |
	| path      | text                  | YES  |     | NULL    |                |
	| st_mode   | mediumint(8) unsigned | YES  |     | NULL    |                |
	| st_uid    | mediumint(8) unsigned | YES  |     | NULL    |                |
	| st_gid    | mediumint(8) unsigned | YES  |     | NULL    |                |
	| date      | datetime              | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('vTree_directories', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('vTree_uid',Integer(unsigned=True)),
		Column('path',Text),
		Column('st_mode',Integer(unsigned=True)),
		Column('st_uid',Integer(unsigned=True)),
		Column('st_gid',Integer(unsigned=True)),
		Column('date',DateTime))
	metadata.create_all(engine)

def create_vTree_files(database):
	""" vTree_files:
	| uid       | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| vTree_uid | mediumint(8) unsigned | YES  |     | NULL    |                |
	| path      | text                  | YES  |     | NULL    |                |
	| filename  | text                  | YES  |     | NULL    |                |
	| content   | longblob              | YES  |     | NULL    |                |
	| st_mode   | mediumint(8) unsigned | YES  |     | NULL    |                |
	| st_uid    | mediumint(8) unsigned | YES  |     | NULL    |                |
	| st_gid    | mediumint(8) unsigned | YES  |     | NULL    |                |
	| date      | datetime              | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('vTree_files', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('vTree_uid',Integer(unsigned=True)),
		Column('path',Text),
		Column('filename',Text),
		Column('st_mode',Integer(unsigned=True)),
		Column('st_uid',Integer(unsigned=True)),
		Column('st_gid',Integer(unsigned=True)),
		Column('date',DateTime))
	metadata.create_all(engine)

def create_dl_projects(database):
	""" dl_projects:
	| uid               | mediumint(8) unsigned                      | NO   | PRI | NULL        | auto_increment |
	| project_uid       | mediumint(8) unsigned                      | YES  |     | NULL        |                |
	| framestore_uid    | mediumint(8) unsigned                      | YES  |     | NULL        |                |
	| project_class     | enum('master','user','template','split')   | YES  |     | user        |                |
	| user_id           | varchar(48)                                | YES  |     | NULL        |                |
	| name              | varchar(255)                               | YES  |     | NULL        |                |
	| cfg_file          | varchar(255)                               | YES  |     | NULL        |                |
	| FrameWidth        | smallint(4) unsigned                       | YES  |     | NULL        |                |
	| FrameHeight       | smallint(4) unsigned                       | YES  |     | NULL        |                |
	| FrameDepth        | enum('8-bit','10-bit','12-bit','12-bit u') | YES  |     | 12-bit      |                |
	| AspectRatio       | decimal(7,4)                               | YES  |     | NULL        |                |
	| ProxyEnable       | enum('true','false')                       | YES  |     | true        |                |
	| ProxyWidthHint    | decimal(6,2)                               | YES  |     | NULL        |                |
	| ProxyDepthMode    | enum('8-bit','SAME_AS_HIRES')              | YES  |     | 8-bit       |                |
	| ProxyMinFrameSize | smallint(4) unsigned                       | YES  |     | NULL        |                |
	| ProxyAbove8bits   | enum('true','false')                       | YES  |     | false       |                |
	| ProxyQuality      | varchar(48)                                | YES  |     | NULL        |                |
	| FieldDominance    | enum('FIELD_1','FIELD_2','PROGRESSIVE')    | YES  |     | PROGRESSIVE |                |
	| VisualDepth       | enum('8-bit','12-bit','unknown')           | YES  |     | 12-bit      |                |
	| SetupDir          | varchar(255)                               | YES  |     | NULL        |                |
	| Description       | text                                       | YES  |     | NULL        |                |
	| status            | enum('active','inactive')                  | YES  |     | active      |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('dl_projects', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('project_uid',Integer(unsigned=True)),
		Column('framestore_uid',Integer(unsigned=True)),
		Column('project_class',String(24)),
		Column('user_id',String(48)),
		Column('name',String(255)),
		Column('cfg_file',String(255)),
		Column('FrameWidth',SmallInteger(unsigned=True)),
		Column('FrameHeight',SmallInteger(unsigned=True)),
		Column('FrameDepth',String(12)),
		Column('AspectRatio',Float(precision=4,asdecimal=True)),
		Column('ProxyEnable',String(12)),
		Column('ProxyWidthHint',Float(precision=2,asdecimal=True)),
		Column('ProxyDepthMode',String(24)),
		Column('ProxyMinFrameSize',SmallInteger(unsigned=True)),
		Column('ProxyAbove8bits',String(12)),
		Column('ProxyQuality',String(48)),
		Column('FieldDominance',String(48)),
		Column('VisualDepth',String(24)),
		Column('SetupDir',String(255)),
		Column('Description',Text),
		Column('status',String(24)))
	metadata.create_all(engine)

def create_framestores(database):
	""" framestores:
	| uid        | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| name       | varchar(128)          | YES  |     | NULL    |                |
	| host       | varchar(128)          | YES  |     | NULL    |                |
	| volume     | varchar(128)          | YES  |     | NULL    |                |
	| partition  | tinyint(1) unsigned   | YES  |     | NULL    |                |
	| host_limit | tinyint(1) unsigned   | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('framestores', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('name',String(128)),
		Column('host',String(128)),
		Column('volume',String(128)),
		Column('partition',SmallInteger),
		Column('host_limit',SmallInteger))
	metadata.create_all(engine)

def create_dl_libraries(database):
	""" dl_libraries:
	| uid            | mediumint(8) unsigned | NO   | PRI | NULL    | auto_increment |
	| framestore_uid |
	| name           | varchar(128)          | YES  |     | NULL    |                |
	| date_modified  |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('dl_libraries', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('framestore_uid',Integer(unsigned=True)),
		Column('name',String(128)),
		Column('date_modified',DateTime))
	metadata.create_all(engine)

def create_ledger(database):
	""" ledger:
	| uid            | mediumint(8) unsigned    | NO   | PRI | NULL    | auto_increment |
	| dl_project_uid | mediumint(8) unsigned    | YES  |     | NULL    |                |
	| user_id        | varchar(48)              | YES  |     | NULL    |                |
	| host           | varchar(16)              | YES  | MUL | NULL    |                |
	| status         | enum('new','run','stop') | YES  |     | NULL    |                |
	| creation_time  | datetime                 | YES  |     | NULL    |                |
	| start_time     | datetime                 | YES  |     | NULL    |                |
	| stop_time      | datetime                 | YES  |     | NULL    |                |
	"""
	engine = sqlalchemy.create_engine('mysql://pyre@localhost/%s' % database)
	metadata = MetaData()
	projects_table = Table('ledger', metadata,
		Column('uid',Integer(unsigned=True), primary_key=True, autoincrement=True),
		Column('dl_project_uid',Integer(unsigned=True)),
		Column('user_id',String(48)),
		Column('host',String(48)),
		Column('status',String(24)),
		Column('creation_time',DateTime),
		Column('start_time',DateTime),
		Column('stop_time',DateTime))
	metadata.create_all(engine)

# put the resolution presets into the resolutions table
def populate_resolutions(database):
	"""
	"""
	rows = [
			[1,'131',640,486,1.3162],
			[2,'NTSC',720,486,1.3333],
			[3,'PAL',720,576,1.3333],
			[4,'PAL HD Anamorphic',720,576,1.7778],
			[5,'Super35 1k',1024,778,1.3162],
			[6,'HD 720',1280,720,1.7778],
			[7,'Academy 2k',1828,1332,1.3723],
			[8,'Scope 2k academy',1828,1556,2.3500],
			[9,'HD 1035',1920,1035,1.8500],
			[10,'HD 1080',1920,1080,1.7778],
			[11,'Film',2048,1556,1.3162],
			[12,'Scope 2k',2048,1556,2.6325],
			[13,'Vista Vision',3072,2048,1.5000],
			[14,'Academy 4k',3656,2664,1.3723],
			[15,'Scope 4k academy',3656,3112,2.3500],
			[16,'Super35 4k',4096,3112,1.3162],
			[17,'Scope 4k',4096,3112,2.6300]
		]
	for row in rows:
		rdb = resolutions(database=database)
		rdb.uid = row[0]
		rdb.name = row[1]
		rdb.width = row[2]
		rdb.height = row[3]
		rdb.aspect = row[4]
		rdb.save()

if __name__ == '__main__':
#	database= 'a52_production'
#	create_projects()
#	create_vTrees()
#	create_vTree_directories()
#	create_vTree_files()
#	database= 'a52_discreet'
#	create_vTree_files(database)
#	create_framestores(database)
#	create_ledger(database)
#	create_resolutions(database)
	database= 'a52_discreet'
	create_dl_libraries(database)
#	populate_resolutions(database)

