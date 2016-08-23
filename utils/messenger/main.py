#!/usr/bin/env python

import smtplib
import os

# google mail servers for a52.com
mail_servers = ['mailhost.a52.com','alt1.aspmx.l.google.com','aspmx.l.google.com','aspmx3.googlemail.com','aspmx2.googlemail.com','alt2.aspmx.l.google.com']

def Email(from_addr,to_addrs,subject,msg,project_id=0,tls=False):
	"""  
	Send a simple email from python
	"""
	# if a project_id is given, and the to_addrs
	# fromt he mailing lists from the project
	# (if there is one)
	if project_id:
		mailing_lists = libdb.get_spyder_mailing_list(project_id)
		if mailing_lists:
			to_addrs = string.join(mailing_lists,",")

	# Add the From:, To: and Subject: headers at the start
	msg = "From: %s\nTo: %s\nSubject:%s\n\n%s" % (from_addr,to_addrs,subject,msg)

	# reform the 'to' addresses into a list
	if type(to_addrs) is not list:
		to_addrs = to_addrs.split(',')

	# connect to the server and send the message
	if tls:
		# TLS login:
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login('a52engineering','2308broadway')
		server.set_debuglevel(1)
	else:
		server = smtplib.SMTP(mail_servers[0])
	server.sendmail(from_addr, to_addrs, msg) 
	server.quit()

def EmailHTML(from_addr,to_addrs,subject,html_file,tls=False):
	"""  
	Send a simple email from python
	"""
	try:
		from email.mime.multipart import MIMEMultipart
		from email.mime.text import MIMEText
	except:
		print "ERROR: Could not import MIME modules"
		return False

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = subject
	msg['From'] = from_addr
	msg['To'] = to_addrs

	# Create the body of the message (a plain-text and an HTML version).
	f = open(html_file,'ro')
	html = f.read()
	f.close
	# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText('', 'plain')
	part2 = MIMEText(html, 'html')

	# Attach parts into message container.
	# According to RFC 2046, the last part of a multipart message, in this case
	# the HTML message, is best and preferred.
	msg.attach(part1)
	msg.attach(part2)

	# connect to the server and send the message
	if tls:
		server = smtplib.SMTP('smtp.gmail.com',587)
		server.ehlo()
		server.starttls()
		server.ehlo()
		server.login('a52engineering','2308broadway')
	else:
		server = smtplib.SMTP(mail_servers[0])
	# sendmail function takes 3 arguments: sender's address, recipient's address
	# and message to send - here it is sent as one string.
	print server.sendmail(from_addr, to_addrs, msg.as_string())
	server.quit()


if __name__ == '__main__':
	#from A52.utils import messenger
	#cwd = os.path.realpath(os.curdir)
	#html_file = "%s/A52/utils/messenger/sample.html" % cwd
	#messenger.EmailHTML('tmy.hooper@gmail.com','tmy.hooper@gmail.com','Framestore stat test',html_file)
	Email('test@a52.com','tmy.hooper@gmail.com,tommy.hooper@a52.com','Final test','last test message')
	pass



