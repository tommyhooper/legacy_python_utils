#!/usr/bin/env python

import commands,os,sys,time
from A52.db.dbcontrol import controller
from A52.utils import dateutil
from A52.utils import dbg
db = controller()

class graph:
	def __init__(self):
		self.rrd_dir = '/Volumes/discreet/lib/ganglia/rrds'
		self.clr = {'sans':{	1:{'line':'#b60000','fill':'#b6000044'},
						2:{'line':'#ec7612','fill':'#ec761244'},
						3:{'line':'#e4c60b','fill':'#e4c60b44'},
						4:{'line':'#249b1e','fill':'#249b1e44'},
						5:{'line':'#aaaaaa','fill':'#aaaaaa44'},
						6:{'line':'#254cf1','fill':'#254cf144'},
						7:{'line':'#3ba699','fill':'#3ba69944'},
						8:{'line':'#8641a9','fill':'#59436544'}
						}
				}
						#5:{'line':'#000000','fill':'#00000044'},
		self.rrdtool = self.find_rrdtool()
		self.get_version()
	
	def find_rrdtool(self):
		"""
		Find the rrdtool executable
		"""
		command = 'which rrdtool'
		which = commands.getoutput(command)
		if os.path.exists(which):
			return which
		if os.path.exists('/usr/bin/rrdtool'):
			return '/usr/bin/rrdtool'
		if os.path.exists('/opt/local/bin/rrdtool'):
			return '/opt/local/bin/rrdtool'
		return None

	def get_version(self):
		"""
		Get the version number from rrdtool
		"""
		out = commands.getoutput(self.rrdtool)
		self.version = out.split()[1]
		self.version_minor = int(self.version.split('.')[1])

	def graph_san(self,host,san_num,width=1600,height=400):
		"""
		Graph the load of one san from all flames
		"""
		days =  10
		seconds = int(days*24*60*60)
		outfile = "san0%d.png -a PNG" % san_num
		args = " --start -%d --end N"  % seconds
		args+= " --width %s --height %s" % (width,height)
		args+= " --title 'SANSTONE0%d' --vertical-label 'Read + Write'" % san_num
		args+= " -E -A"
		args+= " -c BACK#222222"
		args+= " -c CANVAS#222222"
		args+= " -c MGRID#eeeeee"
		args+= " -c FONT#eeeeee"
		args+= " 'DEF':'r0=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_read_L0:AVERAGE'" % (self.rrd_dir,host,host,san_num)
		args+= " 'DEF':'r1=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_read_L1:AVERAGE'" % (self.rrd_dir,host,host,san_num)
		args+= " 'DEF':'w0=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_writen_L0:AVERAGE'" % (self.rrd_dir,host,host,san_num)
		args+= " 'DEF':'w1=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_writen_L1:AVERAGE'" % (self.rrd_dir,host,host,san_num)
		args+= " 'LINE':'r0#83c888:SANSTONE%02d-00-read'" % (san_num)
		args+= " 'AREA':'r0#83c88855'"
		args+= " 'LINE':'r1#3c5c3e:SANSTONE%02d-01-read'" % (san_num)
		args+= " 'AREA':'r1#3c5c3e55'"
		args+= " 'LINE':'w0#7d9398:SANSTONE%02d-00-write'" % (san_num)
		args+= " 'AREA':'w0#7d939855'"
		args+= " 'LINE':'w1#3f4a4d:SANSTONE%02d-01-write'" % (san_num)
		args+= " 'AREA':'w1#3f4a4d55'"
#		i = 1
#		hosts = ['flame1','flame2','flame3','flame4','flame5','flare1','smoke2']
#		for host in hosts:
#			args+= " 'DEF':'h%s_r0=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_read_L0:AVERAGE'" % (i,self.rrd_dir,host,host,san_num)
#			args+= " 'DEF':'h%s_r1=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_read_L1:AVERAGE'" % (i,self.rrd_dir,host,host,san_num)
#			args+= " 'DEF':'h%s_w0=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_writen_L0:AVERAGE'" % (i,self.rrd_dir,host,host,san_num)
#			args+= " 'DEF':'h%s_w1=%s/%s.a52.com/%s_sanstone0%s.rrd:bytes_writen_L1:AVERAGE'" % (i,self.rrd_dir,host,host,san_num)
##			args+= " 'CDEF':'h%s=h%s_w0,h%s_w1,+,h%s_r0,+,h%s_r1,+'" % (i,i,i,i,i)
#			args+= " 'LINE':'h%s_r0%s:SANSTONE%02d-read'" % (i,self.clr['sans'][i]['line'],i)
#			args+= " 'AREA':'h%s_r1%s'" % (i,self.clr['sans'][i]['fill'])
#			args+= " 'LINE':'h%s_w0%s:SANSTONE%02d-write'" % (i,self.clr['sans'][i]['line'],i)
#			args+= " 'AREA':'h%s_w0%s'" % (i,self.clr['sans'][i]['fill'])
#			i+=1
#		i = 1
#		for host in hosts:
#			#args+= " 'AREA':'h%d%s:%s'" % (i,self.clr['sans'][i]['fill'],host)
#			args+= " 'AREA':'h%d%s:%s'" % (i,self.clr['sans'][i]['fill'],host)
#			i+=1
		if self.version_minor >= 4:
			command = "%s graph %s --border 0 %s" % (self.rrdtool,outfile,args)
		else:
			command = "%s graph %s %s" % (self.rrdtool,outfile,args)
		print "COMMAND:",command
		os.system(command)
	
	def concurrent_users(self,start=None,outfile=None,width=800,height=200,title=None,sanstones=[1,2,3,4,5,6,7,8],border=True):
		"""
		Graph the concurrent users of each stone
		"""
		if not start:
			start = 1301265595
		if not outfile:
			outfile = "rrdtest.png"
		if not title:
			title = "Framestore Concurrent Users"
		args = " --start %s" % start
		args+= " --end N --width %d --height %d" % (width,height)
		args+= " --title '%s' --vertical-label Users" % title
		args+= " --lower-limit 0 --upper-limit 7"
		args+= " -E"
		args+= " -c BACK#222222"
		args+= " -c CANVAS#222222"
		args+= " -c MGRID#9c9c9c"
		args+= " -c FONT#eeeeee"
		for n in sanstones:
			args+= " 'DEF':'s%s_users=%s/framestores/sanstone%02d_concurrent_users.rrd:concurrent_users:MAX'" % (n,self.rrd_dir,n)
			args+= " 'LINE':'s%s_users%s:SANSTONE%02d'" % (n,self.clr['sans'][n]['line'],n)
			args+= " 'AREA':'s%s_users%s'" % (n,self.clr['sans'][n]['fill'])
		# RHEL4 does not have the border option
		if self.version_minor >= 4:
			command = "%s graph %s -a PNG --border 0 %s" % (self.rrdtool,outfile,args)
		else:
			command = "%s graph %s -a PNG %s" % (self.rrdtool,outfile,args)
		dbg("COMMAND: %s" % (command),3)
		commands.getoutput(command)
		#os.system(command)
			
	
if __name__ == '__main__':
	g = graph()
	#g.version()
#	for i in range(1,7,1):
#		g.graph_san(i)
#	abs_start = 1300983819
#	start = abs_start
#	ts = time.time()
#	start = int(ts) - (60*60*24*14)
#	print "START:",start
#	for i in range(1,9,1):
#		g.graph_san('flame%s' % i,i)
#	pass
	start = int(time.time()) - (3600*24*1)
	g.concurrent_users(start=start,outfile='test.png',border=False)
	#g.concurrent_users(start=start,outfile='flame04.png',sanstones=[4],border=False)








