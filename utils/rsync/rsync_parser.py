#!/usr/bin/python

import os,sys
import popen2
from select import select
import time
import commands

fmt = "--out-format='::%l:%f'"
command = "rsync -avn --stats %s /usr/discreet /tmp/ " % (fmt)
output = commands.getoutput(command)
for line in output.split("\n"):
	if "Number of files:" in line:
		files_total = int(line.split(':')[1].strip())
	if "Number of files transferred:" in line:
		files_transferred = int(line.split(':')[1].strip())
	if "Total file size:" in line:
		total_bytes = int(line.split(':')[1].strip().split(' ')[0])

print "TOTAL FILES:",files_total
print "FILES TRANSFERRED:",files_transferred
print "TOTAL BYTES:",total_bytes
"""
Number of files: 11869
Number of files transferred: 3051
Total file size: 2839618294 bytes
Total transferred file size: 1067200611 bytes
Literal data: 0 bytes
Matched data: 0 bytes
File list size: 226604
File list generation time: 0.085 seconds
File list transfer time: 0.000 seconds
Total bytes sent: 247044
Total bytes received: 20444
"""

command = "rsync -av --stats %s /usr/discreet /tmp/ " % (fmt)
job = popen2.Popen4(command,0)
#bytes_remaining = total_bytes
bytes_transferred = 0.0
while job.poll() == -1:
	# capture the output of the command
	# for this command it's not necessary
	# to show the output
	sel = select([job.fromchild], [], [], 0.05)
	if job.fromchild in sel[0]:
		output = os.read(job.fromchild.fileno(), 16384),
		for line in output[0].split("\n"):
			if line[0:2] == '::':
				bytes = int(line.split(':')[2])
				file = line.split(':')[3]
				bytes_transferred += bytes
				percent_done = int(round((bytes_transferred / total_bytes)*100,0))
				print "Complete: %s%%\r" % percent_done,
		sys.stdout.flush()
	time.sleep(0.01)



"""
%a the remote IP address
%b the number of bytes actually transferred
%B the permission bits of the file (e.g. rwxrwxrwt)
%c the checksum bytes received for this file (only when sending)
%f the filename (long form on sender; no trailing lq/rq)
%G the gid of the file (decimal) or lqDEFAULTrq
%h the remote host name
%i an itemized list of what is being updated
%l the length of the file in bytes
%L the string lq -> SYMLINKrq, lq => HARDLINKrq, or lqrq (where SYMLINK or HARDLINK is a filename)
%m the module name
%M the last-modified time of the file
%n the filename (short form; trailing lq/rq on dir)
%o the operation, which is lqsendrq, lqrecvrq, or lqdel.rq (the latter includes the trailing period)
%p the process ID of this rsync session
%P the module path
%t the current date time
%u the authenticated username or an empty string
%U the uid of the file (decimal)
"""
