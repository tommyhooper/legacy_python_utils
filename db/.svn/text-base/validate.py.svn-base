
from datetime import datetime
from A52.utils import stringutil
from A52.utils import dateutil
import re


class ValidateError(Exception):
	pass

class RecordExists(Exception):
	pass


class valid:
	

	def __init__(self):
		pass

	def validate(self):
		"""
		Validate every field in self.data 
		using the self.VALIDATION that is 
		defined in each model
		"""
		# first check for a unique key
		self.unique_key()

		if 'VALIDATION' not in dir(self):
			return True
		# fill in defaults for missing attributes that have them
		self.fill_defaults()
		# next check the existing attributes
		for k,v in self.data.iteritems():
			if self.VALIDATION.has_key(k):
				reqs = self.VALIDATION[k]
				#print "Validating:",k,v,reqs
				result = self._requires(k,v,reqs)
				if result:
					return result
		# check for missing required attributes
		return self.required_missing()

	def unique_key(self):
		"""
		if UNIQUE_KEY is set check the fields
		it defines for existing values in the db
		NOTE: This is handled by the save method in the orm
		"""
		if 'UNIQUE_KEY' not in dir(self):
			return True
		if self.data.has_key('uid') and\
		   self.data['uid']:
		   	return True
		kwargs = {}
		for field in self.UNIQUE_KEY:
			if self.data.has_key(field):
				kwargs[field] = self.data[field]
		exists = self.find(**kwargs)
		if exists:
			raise RecordExists,"Record already exists"
		return True

	def fill_defaults(self):
		"""
		Create attributes for missing fields that have
		a default defined in self.VALIDATION
		"""
		for field,reqs in self.VALIDATION.iteritems():
			if reqs.has_key('default'):
				default = self._get_default(reqs)
				if not self.data.has_key(field):
					self.data[field] = default
				elif self.data[field] == None:
					self.data[field] = default

	def required_missing(self):
		"""
		Look for missint attributes that are defined as
		'required' in self.VALIDATION
		"""
		for field,reqs in self.VALIDATION.iteritems():
			if self._is_required(reqs):
				if not self.data.has_key(field):
					raise ValidateError, """%s is missing and is required""" % (field)
		return True

	def _requires(self,k,v,reqs):
		# first check the type
		if reqs['type'] == 'string':
			# test if v is a 'string' or 'unicode'
			if not self._is_string(v):
				raise ValidateError, """%s: "%s" is not a string or unicode""" % (k,v)
			# if this field is required, check if it's empty
			if self._is_empty(v):
				if self._is_required(reqs):
					raise ValidateError, """%s is required but is empty or None""" % (k)
				if self._has_default(v,reqs):
					self.data[k] = self._get_default(reqs)
			else:
				# v has a value, clean it first then finish the tests
				if self._cleanString(reqs):
					v = stringutil.clean_string(v)
					self.data[k] = v
				if self._has_re(reqs):
					if not self._run_re(v,reqs):
						raise ValidateError, """%s: "%s" is invalid""" % (k,v)
				if v == 'undefined':
						raise ValidateError, """%s: "%s" is invalid""" % (k,v)
		if reqs['type'] == 'datetime':
			if not self._is_datetime(v):
				date_time = dateutil.date_from_string(v)
				if date_time:
					self.data[k] = date_time
				else:
					raise ValidateError, """%s: "%s" is not a date or datetime object""" % (k,v)
		if reqs['type'] == 'int':
			if not self._is_int(v):
				raise ValidateError, """%s: "%s" is not a integer""" % (k,v)
		if reqs['type'] == 'float':
			if not self._is_float(v):
				raise ValidateError, """%s: "%s" is not a float""" % (k,v)
		if reqs['type'] == 'boolean':
			bool_cnv = self._convert_boolean(v)
			if bool_cnv in [0,1]:
				self.data[k] = bool_cnv
			else:
				raise ValidateError, """%s: "%s" is not boolean""" % (k,v)
		if reqs['type'] == 'user':
			if not self._is_user(v):
				raise ValidateError, """%s: "%s" is not a valid user""" % (k,v)
		if reqs['type'] == 'project':
			if not self._is_project(v):
				raise ValidateError, """%s: "%s" is not a valid project""" % (k,v)
		if reqs['type'] == 'framestore':
			if not self._is_framestore(v):
				raise ValidateError, """%s: "%s" is not a valid framestore""" % (k,v)
		if reqs['type'] == 'dlProject':
			if not self._is_dlProject(v):
				raise ValidateError, """%s: "%s" is not a valid dlProject""" % (k,v)
		if reqs['type'] == 'vTree':
			if not self._is_vTree(v):
				raise ValidateError, """%s: "%s" is not a valid vTree""" % (k,v)
		if reqs['type'] == 'enum':
			if not self._is_valid_enum(v,reqs):
				raise ValidateError, """%s: "%s" is not one of %s""" % (k,v,reqs['choices'])
		if reqs['type'] == 'range':
			if not self._in_range(v,reqs):
				raise ValidateError, """%s: "%s" is not in range (%s)""" % (k,v,reqs['range'])
		# finally check for the unique flag
		if self._requires_unique(reqs):
			if not self._is_unique(k,v):
				raise ValidateError, """%s: "%s" is not unique""" % (k,v)

		return True

	def _is_vTree(self,v):
		from A52.vTree import vTree
		tree = vTree.find(uid=v)
		if tree:
			return True
		return False

	def _is_project(self,v):
		from A52.Project import Project
		project = Project.find(uid=v)
		if project:
			return True
		return False

	def _is_framestore(self,v):
		from A52.Framestore import Framestore
		framestore = Framestore.find(uid=v)
		if framestore:
			return True
		return False

	def _in_range(self,v,reqs):
		if not reqs.has_key('range'):
			raise ValidateError,"Missing 'range' declaration"
		low,high = reqs['range']
		if float(v) < float(low) or float(v) > float(high):
			return False
		return True

	def _is_valid_enum(self,v,reqs):
		if not reqs.has_key('choices'):
			raise ValidateError,"Missing 'choices' declaration"
		if v in reqs['choices']:
			return True
		return False

	def _is_dlProject(self,v):
		from A52.dlProject import dlProject
		project = dlProject.find(uid=v)
		if project:
			return True
		return False

	def _is_user(self,v):
		from A52.User import User
		user = User.find(user_id=v)
		if user:
			return True
		return False

	def _cleanString(self,reqs):
		if reqs.has_key('cleanString'):
			if reqs['cleanString']:
				return True
		return False
			
	def _convert_boolean(self,v):
		if type(v) in [str,unicode]:
			# look for 'yes','on','true'
			if v.lower()[0] in ['y','o','t']:
				return 1
		elif type(v) is int:
			if v <= 0:
				return 0
			elif v >= 0:
				return 1
		elif v == True:
			return 1
		elif v == False:
			return 0
	
	def _run_re(self,v,reqs):
		if not re.search(reqs['validate_re'],v):
			return False
		return True
		
	def _has_re(self,reqs):
		if reqs.has_key('validate_re'):
			if type(reqs['validate_re']).__name__ == 'SRE_Pattern':
				return True
		return False

	def _is_unique(self,k,v):
		kwargs = {k:v}
		exist = self.find(**kwargs)
		if exist:
			return False
		return True

	def _requires_unique(self,reqs):
		if reqs.has_key('unique'):
			if reqs['unique'] == True:
				return True
			try:
				if reqs['unique'].lower()[0] == 't':
					return True
			except: pass
		return False

	def _is_float(self,v):
		if type(v) is float:
			return True
		try:
			float(v)
		except:
			return False
		else:
			return True

	def _is_int(self,v):
		if type(v) is int:
			return True
		try:
			int(v)
		except:
			return False
		else:
			return True

	def _is_datetime(self,v):
		if type(v).__name__ == 'datetime':
			return True
		return False

	def _get_default(self,reqs):
		if reqs['default'] == 'now()':
			return datetime.today()
		else:
			return reqs['default']

	def _has_default(self,v,reqs):
		if reqs.has_key('default'):
			return True
		return False

	def _is_required(self,reqs):
		if reqs.has_key('status'):
			if reqs['status'] == 'required':
				return True
		return False

	def _is_empty(self,value):
		if value == '' or value == None:
			return True
		return False

	def _is_string(self,value):
		"""
		Test if 'value' is a string or unicode
		"""
		if type(value) in [str,unicode]:
			return True
		return False

