#!/usr/bin/python
# vim:tabstop=8:softtabstop=2:expandtab:

""" 
A bunch of classes to start up a nice little XMLRPC Server 
just override AfxXMLServer.Daemon then 
server = A52XMLServer.Server(yourdaemon,port=3333)
and you're in business.
"""
__version__ = "$Revision: 1.9 $".split()[-2:][0]

from SimpleXMLRPCServer import *
import string
import os
import sys
import syslog
import socket
import array
import datetime
import xmlrpclib
try:
	import decimal
except:
	pass
from types import *


class _shareddata:
	''' shared data to allow gracefull quit '''
	def __init__(self):
		self.quit =0

class _MyHandler(SimpleXMLRPCRequestHandler):
	''' in case we want to log to syslog '''
	def log_message(self, format, *args):
		#syslog.syslog(syslog.LOG_DEBUG,"%s - - [%s] %s\n" %
		#    (self.address_string(), self.log_date_time_string(), format%args))
		pass


class _MyServer(SocketServer.TCPServer,SimpleXMLRPCDispatcher):
	''' Override the Server code to allow gracefull quiting '''

	def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler, logRequests=1,data=None):
		self.logRequests = logRequests
		SimpleXMLRPCDispatcher.__init__(self)
		SocketServer.TCPServer.__init__(self, addr, requestHandler)
		self.data = data

	def serve_forever(self):
		while not self.data.quit:
			self.handle_request()
  
	def log_message(self,format,*args):
		''' Override Logging '''
		pass


class _Marshaller(xmlrpclib.Marshaller):
	''' Override the Marshaller to allow_none '''
	def __init__(self, encoding=None, allow_none=1):
		self.memo = {}
		self.data = None
		self.encoding = encoding
		self.allow_none = 1

	def mydump_struct(self, value, write, escape=xmlrpclib.escape):
		i = id(value)
		if self.memo.has_key(i):
			raise TypeError, "cannot marshal recursive dictionaries"
		self.memo[i] = None
		dump = self.__dump
		write("<value><struct>\n")
		for k, v in value.items():
			write("<member>\n")
			if type(k) is not StringType:
				if unicode and type(k) is UnicodeType:
					k = k.encode(self.encoding)
				else:
					k = str(k)
			write("<name>%s</name>\n" % escape(k))
			dump(v, write)
			write("</member>\n")
		write("</struct></value>\n")
		del self.memo[i]

	def dump_datetime(self,value, write):
		write("<value><string>")
		write(xmlrpclib.escape(str(value)))
		write("</string></value>\n")

	def mydump_long(self, value, write):
		write("<value><int>")
		write(str(int(value)))
		write("</int></value>\n")

	def dump_decimal(self, value, write):
		write("<value><double>")
		write(str(value))
		write("</double></value>")

	def dump_arrayarray(self, value, write):
		write("<value><double>")
		write(value.tostring())
		write("</double></value>")

class Daemon:
	''' the base Class that get overriden as the main code '''
	def __init__(self,data):
		self.serverdata=data

	def kill(self):
		print "Received Kill"
		self.serverdata.quit =1
  
class Server:
	''' Our server.  '''
	def __init__(self,daemon,hostname="",port=8888,aclass=1,allow_reuse_address=True):
		self.data = _shareddata()
		xmlrpclib.Marshaller=_Marshaller
		try:
			xmlrpclib.Marshaller.dispatch[decimal.Decimal]=_Marshaller.dump_decimal
		except:pass
		try:
			xmlrpclib.Marshaller.dispatch[array.array]=_Marshaller.dump_arrayarray
		except:pass
		xmlrpclib.Marshaller.dispatch[type(datetime.date(2005,1,1))]=_Marshaller.dump_datetime
		xmlrpclib.Marshaller.dispatch[type(datetime.datetime(2005,1,1))]=_Marshaller.dump_datetime
		xmlrpclib.Marshaller.dispatch[type(datetime.timedelta(30))]=_Marshaller.dump_datetime
		xmlrpclib.Marshaller.dispatch[DictType]=_Marshaller.mydump_struct
		xmlrpclib.Marshaller.dispatch[LongType]=_Marshaller.mydump_long
		SocketServer.TCPServer.allow_reuse_address = allow_reuse_address
		server = _MyServer(('',port),_MyHandler,1,self.data)
		if aclass == 1:
			d = daemon(self.data)
			server.register_instance(d)
		else:
			for func in dir(daemon):
				func_ptr = getattr(daemon,func)
				if func[0]!="_" and type(func_ptr) is FunctionType:
					server.register_function(func_ptr)
		server.register_function(self.kill,"kill")
		server.register_introspection_functions()
		server.serve_forever()

	def kill(self):
		print "Received Kill"
		self.data.quit =1
  
class StartServer:
	def __init__(self,MyServer,Port,Name,aclass=1):
		try:
			pid = os.fork()
		except OSError, details:
			self.Exit('fork failed', details)
		if pid !=0:
			sys.exit(0)    # kill the parent
		os.setsid()
		os.chdir("/")
		os.umask(2)
		# Do a double fork....
		try:
			pid = os.fork()
		except OSError, details:
			self.Exit('fork failed', details)
		if pid !=0:
			sys.exit(0)    # kill the parent
		#sys.stdin.close()
		sys.stdout = self
		sys.stderr = self
		# Close FDs.
		for fd in range(1024):
			try:
				os.close(fd)
			except OSError:
				pass
		# here's the server....
		try:
			pidf = open("/var/run/%s.pid"%Name.lower(), "w")
			pidf.write("%d" % os.getpid())
			pidf.close()
		except IOError, details:
			print details
			sys.exit(1)
		syslog.openlog(Name, syslog.LOG_PID, syslog.LOG_LOCAL7)
		syslog.syslog(syslog.LOG_INFO, "%s Started" % Name)
		server = Server(MyServer,"",Port,aclass)
		print "%s Exited" % Name

	def write(self,msg):
		if ( msg.strip() != "" ):
			syslog.syslog(syslog.LOG_INFO, msg.strip())  

	def error(self,msg,details=None):
		if details != None:
			msg = '%s:  %s' % (msg, details)
		if ( msg.strip() != "" ):
			syslog.syslog(syslog.LOG_INFO, msg.strip())  

class A52Server:
	def __init__(self):
		import a52
		StartServer(a52,8855,"A52",0);

