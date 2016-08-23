import MySQLdb
from MySQLdb.cursors import DictCursor
from dbcontrol import controller
from A52 import environment

class dbConnect:
	# if you store connections in this cache then python will not close them on py script exit.
	#_CONNECTION_CACHE = {}
    
#	@staticmethod
	def connection(**kwargs):
		"""
		if connection name is specified look for the connection in the cache
		"""
		if kwargs.has_key('connection_name'):
			#if kwargs['connection_name'] in dbConnect._CONNECTION_CACHE:
			#    return dbConnect._CONNECTION_CACHE[kwargs['connection_name']]
			settings = environment.db_settings_for_context(kwargs['connection_name'])
			db = settings['db']
			username = settings['username']
			passwd = settings['password']
			host = settings['host']
			#print "ORM: Connecting to: %s as %s" % (host,username)
			connection = MySQLdb.connect(cursorclass=DictCursor, host=host, user=username, passwd=passwd, db=db)
			#dbConnect._CONNECTION_CACHE[kwargs['connection_name']] = connection
		else:
	            # assume standard connection
			connection = MySQLdb.connect(**kwargs)
		#connection.autocommit(True)
		return connection
    
#    @staticmethod
	def query_connection(connection_name, sql, args=None, auto_commit=True):
		connection = dbConnect.connection(connection_name=connection_name)
		try:
			cursor = connection.cursor()
			cursor.execute(sql, args)
			if auto_commit:
				connection.commit()
			connection.close()
			return cursor
		except MySQLdb.Error, e:
			msg = "MySQLdb Error: Unable to perform sql = '%s', error = %s" % (sql, e)
			print msg
			raise Exception(msg)
		except Exception, e:
			msg = "Unable to perform sql = '%s', error = %s" % (sql, e)
			print msg
			raise Exception(msg)
        
#	@staticmethod
	def escape(val):
		return MySQLdb.escape_string(val)
   
	connection = staticmethod(connection)
	query_connection = staticmethod(query_connection)
	escape = staticmethod(escape)
