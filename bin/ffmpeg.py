#!/usr/bin/python

import threading
import os
import commands
import Queue
import time
import sys
import datetime
import glob
import re
import random
import string
import popen2 # Deprecated ./fuse_2011.py:5: DeprecationWarning: The popen2 module is deprecated.  Use the subprocess module.
import select as Select
import smtplib
import os
import shutil
#from A52.utils import messenger

from optparse import OptionParser
p = OptionParser()
p.add_option("-a",dest='audiofile', type='string',help="audio file")
p.add_option("-o",dest='outfile', default='hoc.mov',type='string',help="name of output file")
p.add_option("-k",dest='keyframe', default=None,type='int',help="force a keyframe every 'x' frames")
p.add_option("-e",dest='encoder', default='h264',type='string',help="encoder type: h264, prores, mpeg2 or mpeg2ts (default = h264)")
p.add_option("-t",dest='thread_num', default=2,type='int',help="number of threads to use for encoding (default:2)")
p.add_option("-c",dest='count', default=None,type='int',help="number of frames to encode (default: all frames found)")
p.add_option("-b",dest='batch_size', default=None,type='int',help="For 2.5k source frames: number of frames to process in a batch (default: None (process all frames))")
p.add_option("-d",dest='resize_dir', type='string',help="For 2.5k source frames: directory to use for resize processing (default: same as 2560x1280 directory)")
p.add_option("-p",dest='pickup', default=None,type='int',help="For Resizing only: picks up processing a resize at the given value")
options,args = p.parse_args()


def help():
	print "\n usage: %s [-a audiofile] [-e encoder (default h264)] [-o outfile (default hoc.mov)] infile start end\n" % (os.path.split(sys.argv[0])[1])


def Email(subject,msg,from_addr='magic_button@a52.com',to_addrs='HOC@a52.com'):
	"""  
	Send a simple email from python
	"""
	# Add the From:, To: and Subject: headers at the start
	msg = "From: %s\nTo: %s\nSubject:%s\n\n%s" % (from_addr,to_addrs,subject,msg)

	# reform the 'to' addresses into a list
	if type(to_addrs) is not list:
		to_addrs = to_addrs.split(',')

	# connect to the server and send the message
	server = smtplib.SMTP('mailhost.a52.com')
	server.sendmail(from_addr, to_addrs, msg) 
	server.quit()


def ffmpeg(command):
	"""
	Run the ffmpeg process and stream the output to the shell
	"""
	job = popen2.Popen4(command,0)
	while job.poll() == -1:
		# capture the output of the command
		# for this command it's not necessary
		# to show the output
		sel = Select.select([job.fromchild], [], [], 0.05)
		if job.fromchild in sel[0]:
			output = os.read(job.fromchild.fileno(), 16384),
			print "%s\r" % output[0],
			sys.stdout.flush()
		time.sleep(0.01)

	# flush any possible info stuck in the buffer
	output = os.read(job.fromchild.fileno(), 16384)
	try:
		print output[0],
		sys.stdout.flush()
	except:pass
	print "\n"
	if job.poll():
		pass
		# got an error status bac
		#print "\n>>> Caught Error: %s\n" % job.poll()
	else:
		pass
		# inferno exited normally
		#print "\n>>> Normal Exit: %s\n" % job.poll()

def get_hoc_h264_ffmpeg(infile,outfile,audio=None,title=None,threads=2,count=None):
	"""
	Return the ffmpeg command to create an
	H264 for House of Cards
	"""
	if title:
		_title = '-metadata title="%s" ' % title
	else:
		_title = ''
	if audio:
		_audio = ' '.join([	
						#'-ar 48000',
						#'-f s16be',
						#'-ac 2',
						'-i %s' % audio,
						'-acodec libfaac',
						'-ab 128000',
						'-ac 2',
						#'-ar 44100',
						#'-strict experimental',
					])
	else:
		_audio = ''

	# the default minimum keyframe = 5
	# and the default max keyframe = 250
	#keyint_min,gop = (5,250)
	# however we're going to make our default 4 
	# for both since that seems to be the best
	# comprimise for allowing better scrubbing
	keyint_min,gop = (8,8)
	if options.keyframe:
		keyint_min = options.keyframe
		gop = options.keyframe

	if count:
		_count = '-vframes %d' % count
	else:
		_count = ''
	

	# ffmpeg works so long as we force the pix_fmt to yuv420p
	ff_cmd = '/opt/ffmpeg-0.11.1/bin/ffmpeg'
	#ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	#ff_cmd = '/var/www/cgi-bin/WiretapCentral/ffmpeg'
	_args = [	
			"-f image2",
			'-s 1920x1080',
			'-r 24000/1001',
			"-i %s" % infile,
			_count,
			'-y',
			_audio,
			'-vcodec libx264',
			_title,
			'-s 1920x1080',
			'-r 24000/1001',
			'-threads %d' % threads,
			'-pix_fmt yuv420p',
			'-me_method hex',
			'-direct-pred 1',			# added back in
			'-coder 0',
			'-me_range 12', 
			'-rc_eq "blurCplx^(1-qComp)" ',
			'-g %d' % gop,
			'-keyint_min %d ' % keyint_min,
			'-sc_threshold 40',
			'-i_qfactor 0.71428572',
			'-b_qfactor 0.76923078', 
			'-b_strategy 1', 
			#'-qcomp 0.6',
			'-qcomp 0.9',
			'-qmin 10', 
			'-qmax 51', 
			'-qdiff 4',
			'-subq 5',
			'-partitions +parti4x4+partp8x8+partb8x8',
			'-bidir_refine 0',
			'-cmp 1',
			# PIX testing: set references to 1
			# and bframes off
			#'-refs 1',
			#'-bf 0',
			'-bf 1',
			'-fast-pskip 1',			# added back in
			'-flags', 				# added for deblocking
			'+loop',				#  "     "      "
			'-deblock 0:0',		# deblock alpha:beta
			#'-deblockbeta 0',			# added back in
			'-crf 23',
			#'-bufsize 2670k',
			'-minrate 10000k',
			'-maxrate 10000k',
			'-vb 10000k',
			'-muxrate 10000k',
			]

	cmd = "%s %s" % (ff_cmd,' '.join(_args))
	meta_cmd = re.sub('[()]',lambda x: "\\%s" % x.group(0),cmd)
	full_cmd = """%s -metadata "comment=%s" %s """ % (cmd,meta_cmd,outfile)
	return full_cmd

	_pix_args = [
			"-f image2",
			'-s 1920x1080',
			'-r 24000/1001',
			"-i %s" % infile,
			_count,
			'-y',
			_audio,
			'-vcodec libx264',
			_title,
			'-s 1920x1080',
			'-r 24000/1001',
			'-threads %d' % threads,
			'-pix_fmt yuv420p',
			# video:
			'-b:v 8000000',
			'-coder 0',
			'-flags', 
			'+loop',
			'-cmp',
			'+chroma',
			'-partitions +parti8x8+parti4x4+partp8x8+partb8x8',
			'-me_method umh',
			'-subq 8',
			'-me_range 16',
			# keyframes:
			'-g %d' % gop,
			'-keyint_min %d' % keyint_min,
			# the rest...
			'-sc_threshold 40',
			'-i_qfactor 0.71',
			'-qcomp 0.6',
			'-qmin 10',
			'-qmax 51',
			'-qdiff 4',
			'-bf 0',
			'-refs 3',
			'-direct-pred 1',
			'-trellis 0',
			'-b-pyramid normal',
			'-mixed-refs 1',
			'-wpredp 1',
			'-8x8dct 0',
			'-fast-pskip 1',
			'-crf 22'
			]

	#cmd = "%s %s" % (ff_cmd,' '.join(_pix_args))
	#meta_cmd = re.sub('[()]',lambda x: "\\%s" % x.group(0),cmd)
	#full_cmd = """%s -metadata "comment=%s" %s """ % (cmd,meta_cmd,outfile)
	#return full_cmd

	"""
	ffmpeg settings from PIX:

	ffmpeg -y -i 'IN.mov'  
	-acodec libfaac -ab '128000' -ac '2' 
	-vcodec libx264 -s '1920x1080' -b '8000000' '-coder' '0' '-flags' '+loop' '-cmp' '+chroma' '-partitions' '+parti8x8+parti4x4+partp8x8+partb8x8' '-me_method' 'umh' '-subq' '8' '-me_range' '16' '-g' '48' '-keyint_min' '25' '-sc_threshold' '40' '-i_qfactor' '0.71' '-qcomp' '0.6' '-qmin' '10' '-qmax' '51' '-qdiff' '4' '-bf' '0' '-refs' '3' '-directpred' '1' '-trellis' '0' '-flags2' '+bpyramid+mixed_refs+wpred-dct8x8+fastpskip' '-wpredp' '0' '-crf' '22' OUT.mov	

	For these encodes I would try setting references to 1 and keyframes every 4 frames. The source audio is already to spec, so you can just copy that audio rather than re-encoding it. Let us know if you have any questions. 


	"""

def get_hoc_prores_ffmpeg(infile,outfile,audio=None,threads=2,count=None):
	"""
	Return the ffmpeg command to create an
	apple prores for House of Cards
	"""
	if audio:
		_audio = ' '.join([
				#'-ar 48000',
				#'-f s16be',
				#'-ac 2',
				'-i %s' % audio,
				#'-ab 128kb',
				'-ar 44100',
				'-strict experimental',
				])
	else:
		_audio = ''

	if count:
		_count = '-vframes %d' % count
	else:
		_count = ''
	
	ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	_args = [ 
			"-f image2",
			'-s 1920x1080',
			'-r 24000/1001',
			"-i %s" % infile,
			_count,
			_audio,
			'-y',
			'-s 1920x1080',
			'-r 24000/1001',
			'-threads %d' % threads,
			'-vcodec prores',
			'-pix_fmt yuv444p10'
			#'-b 100Mb'
			#'-qscale 1'
		]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)


def get_hoc_prores_LT_ffmpeg(infile,outfile,audio=None,threads=2,count=None):
	"""
	Return the ffmpeg command to create an
	apple prores for House of Cards
	"""
	if audio:
		_audio = ' '.join([
				#'-ar 48000',
				#'-f s16be',
				#'-ac 2',
				'-i %s' % audio,
				#'-ab 128kb',
				'-ar 44100',
				'-strict experimental',
				])
	else:
		_audio = ''

	if count:
		_count = '-vframes %d' % count
	else:
		_count = ''
	
	ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	_args = [ 
			"-f image2",
			'-s 1920x1080',
			'-r 24000/1001',
			"-i %s" % infile,
			_count,
			_audio,
			'-y',
			'-s 1920x1080',
			'-r 24000/1001',
			'-threads %d' % threads,
			'-vcodec prores',
			'-profile lt',
#			'-pix_fmt yuv444p10'
			#'-b 80Mb',
			'-qscale 15'
		]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)




def get_hoc_netflix_ffmpeg(infile,outfile,audio=None,threads=2,count=None,ts=True):
	"""
	Create either a transport stream or regular mpeg2 for NetFlix.
	ts = transport stream (True | False)

	# NOTES: High Profile ID, High Format ID
	1920 pels/line
	1152 lines/frame
	60 frames/s
	62.7 Msamples/s
	83.5 Msamples/s*
	100 Mbit/s for 3 layers

	# my 7 min test settings:
	ffmpeg -threads 2 -f image2 -r 24 -i hoc.%07d.dpx -i hoc.aiff -g 1 -bufsize 4000k -vb 80M -minrate 80M -maxrate 80M -muxrate 80M -qscale 1 -s 1920x1080 -dc 10 -vcodec mpeg2video -pix_fmt yuv422p -acodec pcm_s16le -f mpegts hoc_mpeg2.ts

	# from netflix:
	ffmpeg -threads 2 -f image2 -r 24 -i hoc.%07d.dpx -i hoc.aiff -g 1 -bufsize 4000k -vb 80M -minrate 80M -maxrate 80M -muxrate 80M -profile:v 1 -q:v 1-s 1920x1080 -dc 10 -vcodec mpeg2video -pix_fmt yuv422p -acodec pcm_s16le -f mpegts hoc_mpeg2.ts
	"""
	if audio:
		_audio = ' '.join([
				#'-ar 48000',
				#'-f s16be',
				#'-ac 2',
				'-i %s' % audio,

				# mpeg layer 2 codec
				'-acodec mp2',
				'-ab 384000',
				
				# LPCM
				#'-acodec pcm_s16le',
				#'-ab 1536k',
				# netflix wants 448 layer 1 
				# but we cannot encode layer 1
				# so 384 layer 2 will suffice for now
				#'-ab 448000',
				])
	else:
		_audio = ''

	if count:
		_count = '-vframes %d' % count
	else:
		_count = ''
	
	if ts:
		_format = '-f mpegts'
	else:
		_format = '-f mpeg2video'
		#_format = ''
	
	#ff_cmd = '/opt/ffmpeg-0.11.1/bin/ffmpeg'
	ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	# the discreet ffmpeg can accept the audio as a file
	# and the video as a pipe
	#ff_cmd = '/var/www/cgi-bin/WiretapCentral/ffmpeg'
	_args = [	
			"-f image2",
			'-r 24000/1001',
			'-s 1920x1080',
			"-i %s" % infile,
			_audio,
			_count,
			'-vcodec mpeg2video',
			_format,
			'-pix_fmt yuv422p',
			'-s 1920x1080',
			'-r 24000/1001',
			'-threads %d' % threads,
			# raising the bitrate to 84.2 gives us
			# an 'overall' bitrate of 80Mbps
			'-vb 80M',
			'-muxrate 80M',
			#'-bufsize 512k',
			'-minrate 80M',
			'-maxrate 80M',
			#'-profile:v 1',
			#'-flags sgop',
			#'-g 1',
			#'-q:v 1',
			'-dc 10',
			'-intra',
			'-y',
			]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)

def frame_range(infile):
	filename = infile.split('%')[0]
	filelist = glob.glob("%s*" % filename)
	filelist.sort()
	first = ''.join([x for x in re.match('%s(.*)' % filename,filelist[0]).group(1) if x.isdigit()]).lstrip('0')
	last = ''.join([x for x in re.match('%s(.*)' % filename,filelist[-1]).group(1) if x.isdigit()]).lstrip('0')
	return int(first),int(last)

def extract(infile,outfile,start,end,batch_size=options.batch_size,resize_dir=options.resize_dir):
	"""
	Extracts a center cropped 2050x1025 (2:1) from a 2560x1280 source file
	and resizes it into a letterboxed 1920x1080.

	Since the imcopy command has a bug with using the crop arguement 'fit'
	on dpx's we must do a 2 step resize. 

	This function will process in batches of frames (batch_size) 
	to minimize disk usage.

	Examples:
	imcopy -v -o 255,128 -s 2050,1025 -d 2050,1025 -f tiff -e 8 2560x1280/files.%07d.dpx 2050x1025/s1.%07d.tif 1 80000x
	imcopy -v -d 1920,1080 -k fit 2050x1025/s1.%07d.tif 1920x1080/s2.%07d.tif 1 80000x
	"""
	# determine our destination directories.
	# find the 2560x1280 directory and use it's parent
	# for our 2050x1025 and 1920x1080 directories
	base_dir = infile.split('2560x1280')[0].rstrip('/')
	if resize_dir:
		crop_dir = "%s/%s/2050x1025" % (resize_dir,base_dir)
		hd_dir = "%s/%s/1920x1080" % (resize_dir,base_dir)
		#tmp_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6))	
	else:
		crop_dir = "%s/2050x1025" % base_dir
		hd_dir = "%s/1920x1080" % base_dir
	crop_template = "%s/%%07d.tif" % (crop_dir)
	hd_template = "%s/%%07d.tif" % (hd_dir)

	if not os.path.exists(crop_dir):
		print "   Creating directory: %s" % crop_dir
		os.makedirs(crop_dir)
	if not os.path.exists(hd_dir):
		print "   Creating directory: %s" % hd_dir
		os.makedirs(hd_dir)

	if not batch_size:
		batch_size = end
	for i in range (start,end,batch_size):
		b_start = i
		b_end = i + batch_size - 1
		if b_end > end:
			b_end = end
		
		pct_done = int(round((float(b_start)/end)*100))

		print "   [%d%%] Processing files %s -> %s" % (pct_done,b_start,b_end)

		# step 1: 2.5K -> 2050x1025
		args = "-v -o 255,128 -s 2050,1025 -d 2050,1025 -f tiff -e 8 "
		imcopy(infile,crop_template,b_start,b_end,args)

		# step 2: 2050x1025 -> HD
		args = "-v -d 1920,1080 -k fit"
		imcopy(crop_template,hd_template,b_start,b_end,args)

		# step 3: remove 2050x1025
		for x in range(b_start,b_end+1,1):
			target = crop_template % x
			os.remove(target)
	
	try:
		os.removedirs(crop_dir)
	except:pass

	return hd_template


def imcopy(infile,outfile,start,end,args):
	"""
	Process a sequences of images with imcopy.
	"""
	regx = re.compile("Processing file\[[0-9]+\] (.*) to [0-9]+.")
	command = '/usr/discreet/io/bin/imcopy %s %s %s %s %s' % (args,infile,outfile,start,end)
	_imcopy(command,regx)

def _imcopy(command,regx):
	"""
	Run the imcopy process, parse the output and reformat
	it so it makes more sense
	"""
	job = popen2.Popen4(command,0)
	while job.poll() == -1:
		# capture the output of the command
		sel = Select.select([job.fromchild], [], [], 0.05)
		if job.fromchild in sel[0]:
			output = os.read(job.fromchild.fileno(), 16384),
			try:
				frame = regx.match(output[0]).groups()[0]
				sys.stdout.write("\t%s\r" % os.path.split(frame)[1])
				sys.stdout.flush()
			except:pass
		time.sleep(0.01)
	job.fromchild.close()
	sys.stdout.write("\n")
	sys.stdout.flush()

def migrate(mov_file):
	"""
	Move the given file to the appropriate
	'date' directory on nas0 (for HoC)
	"""
	date_dir = datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d')
	dest_path = '/disks/nas0/CGI/12A181_hoc/output/2d/%s' % (date_dir)
	if not os.path.exists(dest_path):
		os.makedirs(dest_path)
		os.chmod(dest_path,0777)
	if os.path.exists("%s/%s" % (dest_path,mov_file)):
		stamp = datetime.datetime.strftime(datetime.datetime.now(),'%H%M%S')
		safe_name = "%s-%s" % (stamp,mov_file)
		print "\tFile exists! Renaming to %s" % (safe_name)
		os.rename("%s/%s" % (dest_path,mov_file),"%s/%s" % (dest_path,safe_name))
	print "\tCopying to %s" % (dest_path)
	shutil.copy2(mov_file,dest_path)
	os.chmod("%s/%s" % (dest_path,mov_file),0777)
	return dest_path
	

if __name__ == '__main__':

	if len(sys.argv) < 2:
		help()
		sys.exit()

	_start = datetime.datetime.today()
	infile = args[0]
	audiofile = options.audiofile
	outfile = options.outfile
	encoder = options.encoder.lower()
	thread_num = options.thread_num
	start,end = frame_range(infile)
	resize = False
	if options.count:
		count = options.count
	else:
		count = end - start + 1

	# get the width and height of our infile
	try:
		identify = 'identify -format %%w:%%h %s' % (infile % start)
		width,height = [int(x) for x in commands.getoutput(identify).split(':')]
		if (width,height) == (2560,1280):
			resize = True
		elif (width,height) != (1920,1080):
			print "\nError: Invalid width and height (%sx%s)\n" % (width,height)
			sys.exit()
	except:
		width,height = (1920,1080)

	# if the resize flag is set the source files are 2.5k
	# resize the files down to 1920x1080
	if resize:
		# preliminary check for the encoder setting.
		# the resize can take hours so best to check this now:
		if encoder not in ['prores','lt','h264','mpeg2','mpeg2ts']:
			print "\n[41mERROR:[m Unrecognized encoder setting: %s\n" % encoder
			sys.exit()
		print "\n[44mResizing 2.5k -> HD:[m"
		if options.pickup:
			infile = extract(infile,outfile,options.pickup,end)
		else:
			infile = extract(infile,outfile,start,end)

	if encoder == 'prores':
		#tmpfile = "_pr-%s" % outfile
		tmpfile = outfile
		movname = outfile
		command = get_hoc_prores_ffmpeg(infile,tmpfile,audio=audiofile,threads=thread_num,count=count)
	if encoder == 'lt':
		tmpfile = outfile
		movname = outfile
		command = get_hoc_prores_LT_ffmpeg(infile,tmpfile,audio=audiofile,threads=thread_num,count=count)
	if encoder == 'h264':
		tmpfile = "_h2-%s" % outfile
		movname = outfile
		command = get_hoc_h264_ffmpeg(infile,tmpfile,audio=audiofile,threads=thread_num,count=count)
	if encoder in ['mpeg2','mpeg2ts']:
		if os.path.splitext(outfile)[1] != 'mpg':
			outfile = '.'.join([os.path.splitext(outfile)[0],'mpg'])
		tmpfile = outfile
		movname = outfile
		ts = False
		if encoder == 'mpeg2ts':
			ts = True
		command = get_hoc_netflix_ffmpeg(infile,tmpfile,audio=audiofile,threads=thread_num,count=count,ts=ts)

	print "\n[44mCreate FFMPEG:[m"
	print "\t%10s: %s" % ('Encoder',encoder.upper())
	print "\t%10s: %s" % ('Infile',infile)
	print "\t%10s: %s" % ('Start',start)
	print "\t%10s: %s" % ('End',end)
	print "\t%10s: %s" % ('Count',count)
	print "\n[44mCommand:[m \n%s" % (command)
	print ""	

	# start the ffmpeg command
	ffmpeg(command)

	qt_cmd = '/var/www/cgi-bin/WiretapCentral/qt-faststart'
	# process qt-faststart but only for h264
	if encoder == 'h264':
		print "\n[44mMaking H264 faststart...[m"
		qt_command = '%s %s %s' % (qt_cmd,tmpfile,movname)
		print "\t%s" % qt_command
		commands.getoutput(qt_command)

	# form the path on nas0 where this mov/mpg file is going to go:
	print "\n[44mMoving mov/mpg file...[m"
	final_path = migrate(movname)

	# get the elapsed time and email the HOC 
	# mail list that this mov/mpg is done
	_stop = datetime.datetime.today()
	elapsed = _stop-_start
	print "\nElapsed time: %s" % (_stop-_start)
	subject = '%s complete' % (movname)
	msg = '%s created\n' % (movname)
	msg+= 'Path: %s\n' % (final_path)
	msg+= 'Elapsed: %s\n' % (_stop-_start)
	Email(subject,msg,to_addrs='hoc@a52.com')







