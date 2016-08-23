#!/usr/bin/python

import os
import sys
import re
re_seq = re.compile('^(|.*[^0-9])([0-9]+)([^0-9]*)$')


def help():
	print "\n usage: %s search_directory" % (os.path.split(sys.argv[0])[1])


def find_renders(path):
	"""
	Walk the 'path' and find images
	Return a dictionary in this form:
		{'path to cr2 sequence': [list of cr2 files]}
	"""
	images = {}
	print 'Searching in',path
	for root,dirs,files in os.walk(path,followlinks=True):
		for _file in files:
			try:
				images[root].append(_file)
			except:
				images[root] = [_file]
	return images

def get_sequences(files):
	"""
	Takes a list of files and splits it
	into sequences. Returns a list
	of sequences expressed in printf format.
	e.g.
	help060_c02_a22_l06_soldier_bty_soldier.MM_soldier_C.%04d.exr (1-67)

	Returns a dict of:
	'help060_c02_a22_l06_soldier_bty_soldier.MM_soldier_C':
		'padding' : '%04d',
		'ext' : '.exr',
		'frame_numbers' : [0001,0002,0003,0004...],
		'start' : 1,
		'end' : 67,
		'template' : 'help060_c02_a22_l06_soldier_bty_soldier.MM_soldier_C.%04d.exr'
	"""
	regx = re.compile('(.*\.)([0-9]*$)')
	info = {}
	for _file in files:
		full_filename = os.path.basename(_file)
		full_path = os.path.dirname(_file)
		noext,ext = os.path.splitext(full_filename)
		groups = regx.search(noext)
		if groups:
			re_filename = groups.group(1)
			re_file_number = groups.group(2)
			key = "%s%s" % (re_filename,ext)

			if info.has_key(key):
				try:
					info[key]['frame_numbers'].append(re_file_number)
				except:
					info[key]['frame_numbers'] = [re_file_number]
			else:
				info[key] = {	'filename':re_filename,
							'pad':None,
							'start':None,
							'end':None,
							'template':None,
							'ext':ext,
							'frame_numbers':[re_file_number]}

		else:
			if not info.has_key(_file):
				info[noext] = {	'filename':_file,
							'ext':ext,
							'frame_numbers':None}
			else:
				print "Error: %s (%s:%s)" % (_file,noext,ext)

	for key in info:
		if info[key]['frame_numbers']:
			fnums = info[key]['frame_numbers']
			fnums.sort()
			pad = '%%0%dd' % len(fnums[-1])
			start = int(fnums[0].lstrip('0'))
			end = int(fnums[-1].lstrip('0'))
			file_template = "%s%s%s" % (info[key]['filename'],pad,ext)
			info[key]['pad'] = pad
			info[key]['start'] = start
			info[key]['end'] = end
			info[key]['template'] = file_template
	return info

def _get_rv_header(start,end,fps):
	return """GTOa (3)

		rv : RVSession (2)
		{
			session
			{
				string viewNode = "defaultLayout"
				int marks = [ ]
				int[2] range = [ [ %d %d ] ]
				int[2] region = [ [ %d %d ] ]
				float fps = %d 
				int realtime = 0
				int inc = 1
				int currentFrame = %d
				int version = 1
				int background = 0
			}
		}
		\n\n"""	% (start,end+1,start,end+1,fps,start)

def _get_rv_sequence(event_no,path,filename,file_template,start,end,fps,width,height):
	return """
		sourceGroup%06d: RVSourceGroup (1)
		{
			ui
			{
				string name = "/%s"
			}
		}
	
		sourceGroup%06d_source : RVFileSource (1)
		{
			media
			{
				string movie = "/%s%s"
			}
	
			group
			{
				float fps = %d
				float volume = 1
				float audioOffset = 0
				int rangeOffset = 0
				int noMovieAudio = 0
				float balance = 0
				float crossover = 0
			}
	
			cut
			{
				int in = -2147483647
				int out = 2147483647
			}
	
			request
			{
				int readAllChannels = 0
				string imageLayerSelection = [ ]
				string imageViewSelection = [ ]
				string imageChannelSelection = [ ]
				string stereoViews = [ ]
			}
	
			proxy
			{
				int[2] range = [ [ %d %d ] ]
				int inc = 1
				int[2] size = [ [ %d %d ] ]
			}
		}
		\n\n""" % (event_no,filename,event_no,path,file_template,fps,start,end+1,width,height)


def build_rv_file(filename,path,sequences,fps=24):
	"""
	Build the sequences into a rv GTO file
	"""
	_file = open(filename,'w')
	starts = []
	ends = []
	for k in sequences.keys():
		starts.append(sequences[k]['start'])
		ends.append(sequences[k]['end'])
	min_start = min(starts)
	max_end = max(ends)
	header_text = _get_rv_header(min_start,max_end,fps)
	_file.write(header_text)

	event_no = 0
	for k in sequences.keys():
		filename = sequences[k]['filename'].rstrip('.')
		file_template = sequences[k]['template']
		start = sequences[k]['start']
		end = sequences[k]['end']
		width= 7777
		height = 8888

		seq_text = _get_rv_sequence(event_no,path,filename,file_template,start,end,fps,width,height)
		event_no+=1
		_file.write(seq_text)
		if event_no == 10:
			break

	_file.close()



if __name__ == '__main__':

	if len(sys.argv) < 2:
		#help()
		#sys.exit()
		path = '/disks/nas0/CGI/12A191_target_holiday_2012/shot/helpers/help060/work.ryan/maya/images/help060_c02_a22_l08_s08/'
	else:
		path = sys.argv[1]

	tree = find_renders(path)
	for root in tree.keys():
		seqs = get_sequences(tree[root])
	build_rv_file('generator_test_mid.rv',path,seqs)
	

