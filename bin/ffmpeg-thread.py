#!/usr/bin/python

import threading
import os
import commands
import Queue
import time
import sys
import datetime
import popen2 # Deprecated ./fuse_2011.py:5: DeprecationWarning: The popen2 module is deprecated.  Use the subprocess module.
import select as Select

from optparse import OptionParser
p = OptionParser()
p.add_option("-a",dest='audiofile', type='string',help="audio file")
p.add_option("-o",dest='outfile', default='hoc.mov',type='string',help="name of output file")
p.add_option("-e",dest='encoder', default='both',type='string',help="encoder type: h264 or prores (default = both)")
p.add_option("-t",dest='thread_num', default=2,type='int',help="number of threads to use for encoding (default:2)")
options,args = p.parse_args()

def help():
	print "\n usage: %s infile start end\n" % (os.path.split(sys.argv[0])[1])

def get_hoc_convert(infile,width,height,encoder=None):
	"""
	Return the convert command for the center extraction
	for House of Cards.

	If encoder is given blackout a section of
	the slate and overlay our own text there.

	Example:
		convert -crop 2050x1025+255+128 -resize 1920x960 -bordercolor '#000000' -border x60 
			HOC_2560X1280_FRAMING_CHART_1_SEC_S0001.0000000.dpx test.png

		Modifying the slate:
			After the common command:
			convert -crop 2050x1025+255+128 -resize 1920x960 -bordercolor "#000000" -border x60 slate.dpx 

		BLACK OUT BOX:
			-stroke "#000000" -strokewidth 2 -fill "#000000" -draw "rectangle 465,533,1225,815"
		ENCODER TYPE TEXT:
			-fill "#ffaa00" -pointsize 52 -gravity northwest -draw "text 715,663 'H264'" 
		DATE TEXT:
			-fill "#ffaa00" -pointsize 52 -gravity northwest -draw "text 715,862 '09.11.2012'"

	"""
	overlay = ''
#	if encoder:
#		# alter the current slate to include
#		# our encoder type and date
#		# date format: 09.11.2012
#		date = datetime.datetime.today().strftime('%m.%d.%Y')
#		overlay = """ -stroke "#000000" -strokewidth 2 -fill "#000000" -draw "rectangle 465,533,1225,815" """
#		overlay+= """ -fill "#ffaa00" -pointsize 52 -gravity northwest -draw "text 715,663 '%s'" """ % encoder
#		overlay+= """ -fill "#ffffff" -pointsize 52 -gravity northwest -draw "text 715,862 '%s'" """ % date

	if width == 1920 and height == 1080:
		_args = []
	elif width == 2560 and height == 1280:
		_args = [	'-crop 2050x1025+255+128',
				'-resize 1920x960',
				'-bordercolor "#000000" ',
				'-border x60']
	else:
		print "\nInvalid width / height: %sx%s\n" % (width,height)
		sys.exit()

	_args.extend([	infile,
				overlay,
				'-depth 8',
				'-set colorspace rgb',
				'rgb:-'
				])
	return "convert %s" % (' '.join(_args))

class ffmpeg(threading.Thread):

	def __init__(self,command,encoder=None):
		self.command = command
		self.encoder = encoder
		threading.Thread.__init__(self)

	def run(self):
		self.job = popen2.Popen4(self.command,0)
		while self.job.poll() == -1:
			# capture the output of the command
			# for this command it's not necessary
			# to show the output
			sel = Select.select([self.job.fromchild], [], [], 0.05)
			if self.job.fromchild in sel[0]:
				output = os.read(self.job.fromchild.fileno(), 16384),
				print "%s\r" % output[0],
				sys.stdout.flush()
			#if self._stopped:
			#	os.kill(self.job.pid,signal.SIGTERM)
			#	break
			time.sleep(0.01)

		# mark that we're no longer running
		self.running = False
		# flush any possible info stuck in the buffer
		output = os.read(self.job.fromchild.fileno(), 16384)
		try:
			print output[0],
			sys.stdout.flush()
		except:pass
		print "\n"
		if self.job.poll():
			pass
			# got an error status bac
			#print "\n>>> Caught Error: %s\n" % self.job.poll()
		else:
			pass
			# inferno exited normally
			#print "\n>>> Normal Exit: %s\n" % self.job.poll()

def get_hoc_h264_ffmpeg(outfile,count,audio=None,title=None,threads=2,infile=None):
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
						'-ar 48000',
						'-f s16be',
						'-ab 128kb',
						'-ac 2',
						'-i %s' % audio,
						'-ar 44100'
					])
	else:
		_audio = ''

	if infile:
		_format = "-f image2"
		_input = "-i %s" % infile
	else:
		_format = '-f rawvideo -pix_fmt rgb24'
		_input = "-i -"
	
	
	#ff_cmd = '/opt/ffmpeg-0.11.1/bin/ffmpeg'
	#ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	# the h264 options are fairly specific to
	# the version discreet is running so it's easier
	# to just use that version for the H264
	ff_cmd = '/var/www/cgi-bin/WiretapCentral/ffmpeg'
	_args = [ 
			_format,
			'-s 1920x1080',
			'-r 24000/1001',
			_input,
			'-y',
			'-s 1920x1080',
			'-r 24000/1001',
			'-vframes %d' % count,
			_title,
			_audio,
			'-vcodec libx264',
			'-r 24000/1001',
			'-threads %d' % threads,
			'-pix_fmt yuv422p',
			'-me_method hex',
			#'-directpred 1',
			'-coder 0',
			'-me_range 12', 
			'-g 250',
			'-rc_eq "blurCplx^(1-qComp)" ',
			'-keyint_min 5',
			'-sc_threshold 40',
			'-i_qfactor 0.71428572',
			'-b_qfactor 0.76923078', 
			'-b_strategy 1', 
			'-qcomp 0.6',
			'-qmin 10', 
			'-qmax 51', 
			'-qdiff 4',
			'-subq 5',
			'-partitions +parti4x4+partp8x8+partb8x8',
			'-bidir_refine 0',
			'-cmp 1',
			#'-flags2 fastpskip',
			#'-deblockalpha 0',
			#'-deblockbeta 0',
			'-bf 1',
			'-crf 23',
			#'-minrate 7700k',
			#'-maxrate 7700k',
			'-vb 7700k',
			'-muxrate 7700k',
		]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)

def get_hoc_prores_ffmpeg(outfile,count,audio=None,threads=2,infile=None):
	"""
	Return the ffmpeg command to create an
	apple prores for House of Cards
	"""
	if audio:
		_audio = ' '.join(['-ar 48000',
				'-f s16be',
				'-ac 2',
				'-i %s' % audio,
				#'-ab 128kb',
				'-ar 44100',
				'-strict experimental',
				])
	else:
		_audio = ''

	if infile:
		_format = "-f image2"
		_input = "-i %s" % infile
	else:
		_format = '-f rawvideo -pix_fmt rgb24'
		_input = "-i -"
	
	ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	_args = [ 
			_format,
			'-s 1920x1080',
			'-r 24000/1001',
			_input,
			_audio,
			'-y',
			'-s 1920x1080',
			'-r 24000/1001',
			'-vframes %d' % count,
			'-threads %d' % threads,
			'-vcodec prores',
			'-pix_fmt yuv444p10'
#			'-b 100Mb'
#			'-qscale 1'
		]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)



def get_hoc_netflix_ffmpeg(outfile,count,audio=None,threads=2,infile=None):
	"""
	# NOTES: High Profile ID, High Format ID
	1920 pels/line
	1152 lines/frame
	60 frames/s
	62.7 Msamples/s
	83.5 Msamples/s*
	100 Mbit/s for 3 layers
	"""
	if audio:
		_audio = ' '.join(['-ar 48000',
				'-f s16be',
				'-ac 2',
				'-i %s' % audio,
				#'-ab 128kb',
				#'-acodec pcm_s16le',
				'-ar 44100',
				'-strict experimental',
				])
	else:
		_audio = ''

	if infile:
		_format = "-f image2"
		_input = "-i %s" % infile
	else:
		_format = '-f rawvideo -pix_fmt rgb24'
		_input = "-i -"
	
	#ff_cmd = '/opt/ffmpeg-0.11.1/bin/ffmpeg'
	ff_cmd = '/opt/ffmbc-0.7rc7/bin/ffmbc'
	# the discreet ffmpeg can accept the audio as a file
	# and the video as a pipe
	#ff_cmd = '/var/www/cgi-bin/WiretapCentral/ffmpeg'
	_args = [	
			_format,
			'-s 1920x1080',
			'-r 24000/1001',
			_input,
			_audio,
			'-y',
			'-s 1920x1080',
			'-r 24000/1001',
			'-vframes %d' % count,
			'-threads %d' % threads,
			'-g 1',
#			'-bufsize 4000k',
#			'-vb 80M',
#			'-minrate 80M',
			'-maxrate 80M',
			'-muxrate 80M',
			'-profile 1',
			'-qscale 1',
			'-s 1920x1080',
			'-dc 10',
			'-vcodec mpeg2video',
			'-pix_fmt yuv422p10',
			'-f mpegts',
			]
	return "%s %s %s" % (ff_cmd,' '.join(_args),outfile)

def convert(infile,start,end,threads,width,height,slate=False):
	"""
	Process the convert command one frame
	at a time and write to the ffmpeg thread.

	Slate range: 240-433
	"""
	# prevent imagemagick from threading as 
	# it actually slows us down for this type
	# of operation (speed increase is roughly 2x)
	os.putenv('MAGICK_THREAD_LIMIT','1')
	count = end-start+1
	for i in range(start,end+1,1):
		target = infile % i
		if slate and (240 < i <= 433):
			for thread in threads:
				command = get_hoc_convert(target,width,height,encoder=thread.encoder)
				#print "\nCOMMAND:%s\n%s\n" % (i,command)
				status,data = commands.getstatusoutput(command)
				thread.job.tochild.write(data)
		else:
			command = get_hoc_convert(target,width,height)
			status,data = commands.getstatusoutput(command)
			for thread in threads:
				thread.job.tochild.write(data)


if __name__ == '__main__':

	if len(sys.argv) < 4:
		help()
		sys.exit()

	infile = args[0]
	start = int(args[1])
	end = int(args[2])
	count = end - start + 1
	audiofile = options.audiofile
	outfile = options.outfile
	encoder = options.encoder.lower()
	thread_num = options.thread_num

	# get the width and height of our infile
	identify = 'identify -format %%w:%%h %s' % (infile % start)
	width,height = [int(x) for x in commands.getoutput(identify).split(':')]
	if (width,height) == (1920,1080):
		# for now just print out the commands for each encoder type
		prores = get_hoc_prores_ffmpeg('_pr-%s' % outfile,count,audio=audiofile,threads=thread_num,infile=infile)
		h264 = get_hoc_h264_ffmpeg('_h2-%s' % outfile,count,audio=audiofile,threads=thread_num,infile=infile)
		mpeg2 = get_hoc_netflix_ffmpeg('_m2-%s' % outfile,count,audio=audiofile,threads=thread_num,infile=infile)
#		
		print "\n--- PRORES --- "
		print prores
#		print "\n--- H264 --- "
#		print h264
#		print "\n--- MPEG2 --- "
#		print mpeg2


	sys.exit()
	clips = []
	if encoder in ['prores','both','all']:
		tmpfile = "_pr-%s" % outfile
		movname = "PRORES-%s" % outfile
		clips.append({
			'tmpfile':tmpfile,
			'movname':movname,
			'encoder':'PRORES 4444',
			'command':get_hoc_prores_ffmpeg(tmpfile,count,audio=audiofile,threads=thread_num)})
	if encoder in ['h264','both','all']:
		tmpfile = "_h2-%s" % outfile
		movname = "H264-%s" % outfile
		clips.append({
			'tmpfile':tmpfile,
			'movname':movname,
			'encoder':'H264',
			'command':get_hoc_h264_ffmpeg(tmpfile,count,audio=audiofile,threads=thread_num)})
	if encoder in ['mpeg2','all']:
		tmpfile = "_m2-%s" % outfile
		movname = "MPEG2-%s" % outfile
		clips.append({
			'tmpfile':tmpfile,
			'movname':movname,
			'encoder':'MPEG2',
			'command':get_hoc_netflix_ffmpeg(tmpfile,count,audio=audiofile,threads=thread_num)})

	i = 1
	ffmpeg_threads = []
	for clip in clips:
		print "\n[44mCommand:[m\n%s\n[34m--------------[m" % clip['command']
		# start the ffmpeg threads
		_thread = ffmpeg(clip['command'],encoder=clip['encoder'])
		_thread.setDaemon(True)
		_thread.start()
		ffmpeg_threads.append(_thread)
		i+=1

	# start the convert loop
	convert(infile,start,end,ffmpeg_threads,width,height,slate=True)

	for clip in clips:
		print "\n\n[44mFile:[m %s" % clip['tmpfile']
	sys.exit()
	qt_cmd = '/var/www/cgi-bin/WiretapCentral/qt-faststart'
	# process qt-faststart but only for h264
	if encoder == 'h264':
		qt_command = '%s %s %s' % (qt_cmd,a_tmp_outfile,a_outfile)
		print qt_command
		commands.getoutput(qt_command)

	if b_cmd:
		qt_command = '%s %s %s' % (qt_cmd,b_tmp_outfile,b_outfile)
		print qt_command
		commands.getoutput(qt_command)



"""
ffmpeg -f image2 -s 1920x1080 -r 24000/1001 -i siz.%04d.dpx -y -s 1920x1080 -r 24000/1001 -ar 48000 -f s16be -ab 128kb -ac 2 -i /Volumes/DH3723SAS01/12A210_HOC_sizzle/audio/Sizzle13_LOCKED_KIRK_V7_PREGRADE_WIP02.aiff -ar 44100 -threads 2 -vcodec libx264 -me_method hex -coder 0 -me_range 12 -g 250 -rc_eq "blurCplx^(1-qComp)"  -keyint_min 5 -sc_threshold 40 -i_qfactor 0.71428572 -b_qfactor 0.76923078 -b_strategy 1 -qcomp 0.6 -qmin 10 -qmax 51 -qdiff 4 -subq 5 -partitions +parti4x4+partp8x8+partb8x8 -bidir_refine 0 -cmp 1 -bf 1 -crf 23 -vb 7700k -muxrate 7700k sizzle_wip07.mov"
"""







