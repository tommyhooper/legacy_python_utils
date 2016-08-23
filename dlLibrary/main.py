
import re,os
from A52.utils import dateutil

class dlLibrary:
	def __init__(self,host,volume,project,library):
		self.host = host
		self.volume = volume
		self.project = project
		self.library = library

	def get_date_modified(self):
		"""
		Get the date modified for the library this
		object represents.
		"""
		path = "/hosts/%s/usr/discreet/clip/%s/%s/%s" % (	host,
											volume,
											project,
											name)
		stats = os.stat(path)
		mod_time = stats.st_mtime
		self.date_modified = dateutil.timestamp_to_datetime(mod_time)
		return self.date_modified

	#@staticmethod
	def validate_library_name(name,only_main=True):
		"""
		Return True if 'name' is a valid
		library name. NOTE: does not mean 
		'name' is actually a library, just
		that the name is a valid library name.
		"""
		if only_main:
			pattern = re.compile('(.*)\.[0]{3}\.(clib)$')
		else:
			pattern = re.compile('(.*)\.[0-9]{3}\.(clib)$')
		regx = re.match(pattern,name)
		if regx:
			return True
		else:
			return False
	validate_library_name = staticmethod(validate_library_name)

	#@staticmethod
	def is_excluded(name):
		"""
		Return True if the library 'name' is one
		of many libraries that should be excluded 
		from archiving - and possibly other functions
		"""
		#master_libs = ['MASTER','IN','OUT','VFX','ELEMENTS','CONFORMS','EDITS','POST','Default','Lost_+_Found']
		exclude_terms = ['Lost_+_Found','ExportIO','_Burn_','_Cache_','Default']
		for term in exclude_terms:
			if name.find(term) != -1:
				return True
		return False
	is_excluded = staticmethod(is_excluded)



if __name__ == '__main__':
#	print dlLibrary.is_excluded('Default_Clip_Library_flare_flare04.flare_flare04.000.clib')
#	l = dlLibrary(name='hello.000.clib',project='test_project',volume='stonefs8',host='ripley')
#	l.create()
#	l.inspect()
#	libraries = dlLibrary.find(host='flame1')
#	print "L:",libraries
#	for l in libraries:
#		l.inspect()
	pass
