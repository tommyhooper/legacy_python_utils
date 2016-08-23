
import os
import bz2
import commands
import socket
from A52.utils import dateutil
from datetime import datetime

class mysql:


	def __init__(self):
		self.databases = ['a52_production','a52_discreet','atempo']
		self.hostname = socket.gethostname()
		self.backup_dir = '/Volumes/discreet/lib/mysql/backup/%s' % self.hostname

	def run(self):
		stamp = dateutil.legible_date(datetime.today(),20)
		for db in self.databases:
			bck_file = "%s/%s/%s_%s" % (self.backup_dir,db,db,stamp)
			command = "mysqldump -u root %s" % (db)
			output = commands.getoutput(command)
			if not os.path.exists("%s.bz2" % bck_file):
				print "Backing up db: %s to %s.bz2" % (db,bck_file)
				bz_file = bz2.BZ2File("%s.bz2" % bck_file,'w')
				bz_file.write(output)
				bz_file.close()

if __name__ == '__main__':
	m = mysql()
	m.run()
