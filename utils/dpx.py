#!/usr/bin/python
import os
import sys
import struct 
import getopt
import types
import string


"""
typedef unsigned int U32;
typedef char ASCII;
typedef unsigned char U8;
typedef unsigned short U16;
typedef float R32;

typedef struct file_information
{
    U32   magic_num;        /* magic number 0x53445058 (SDPX) or 0x58504453 (XPDS) */
    U32   offset;           /* offset to image data in bytes */
    ASCII vers[8];          /* which header format version is being used (v1.0)*/
    U32   file_size;        /* file size in bytes */
    U32   ditto_key;        /* read time short cut - 0 = same, 1 = new */
    U32   gen_hdr_size;     /* generic header length in bytes */
    U32   ind_hdr_size;     /* industry header length in bytes */
    U32   user_data_size;   /* user-defined data length in bytes */
    ASCII file_name[100];   /* iamge file name */
    ASCII create_time[24];  /* file creation date "yyyy:mm:dd:hh:mm:ss:LTZ" */
    ASCII creator[100];     /* file creator's name */
    ASCII project[200];     /* project name */
    ASCII copyright[200];   /* right to use or copyright info */
    U32   key;              /* encryption ( FFFFFFFF = unencrypted ) */
    ASCII Reserved[104];    /* reserved field TBD (need to pad) */
} FileInformation;
typedef struct _image_information
{
    U16    orientation;          /* image orientation */
    U16    element_number;       /* number of image elements */
    U32    pixels_per_line;      /* or x value */
    U32    lines_per_image_ele;  /* or y value, per element */
    struct _image_element
    {
        U32    data_sign;        /* data sign (0 = unsigned, 1 = signed ) */
				 /* "Core set images are unsigned" */
        U32    ref_low_data;     /* reference low data code value */
        R32    ref_low_quantity; /* reference low quantity represented */
        U32    ref_high_data;    /* reference high data code value */
        R32    ref_high_quantity;/* reference high quantity represented */
        U8     descriptor;       /* descriptor for image element */
        U8     transfer;         /* transfer characteristics for element */
        U8     colorimetric;     /* colormetric specification for element */
        U8     bit_size;         /* bit size for element */
       	U16    packing;          /* packing for element */
        U16    encoding;         /* encoding for element */
        U32    data_offset;      /* offset to data of element */
        U32    eol_padding;      /* end of line padding used in element */
        U32    eo_image_padding; /* end of image padding used in element */
        ASCII  description[32];  /* description of element */
    } image_element[8];          /* NOTE THERE ARE EIGHT OF THESE */

    U8 reserved[52];             /* reserved for future use (padding) */
} Image_Information;

typedef struct _image_orientation
{
    U32   x_offset;               /* X offset */
    U32   y_offset;               /* Y offset */
    R32   x_center;               /* X center */
    R32   y_center;               /* Y center */
    U32   x_orig_size;            /* X original size */
    U32   y_orig_size;            /* Y original size */
    ASCII file_name[100];         /* source image file name */
    ASCII creation_time[24];      /* source image creation date and time */
    ASCII input_dev[32];          /* input device name */
    ASCII input_serial[32];       /* input device serial number */
    U16   border[4];              /* border validity (XL, XR, YT, YB) */
    U32   pixel_aspect[2];        /* pixel aspect ratio (H:V) */
    U8    reserved[28];           /* reserved for future use (padding) */
} Image_Orientation;

typedef struct _motion_picture_film_header
{
    ASCII film_mfg_id[2];    /* film manufacturer ID code (2 digits from film edge code) */
    ASCII film_type[2];      /* file type (2 digits from film edge code) */
    ASCII offset[2];         /* offset in perfs (2 digits from film edge code)*/
    ASCII prefix[6];         /* prefix (6 digits from film edge code) */
    ASCII count[4];          /* count (4 digits from film edge code)*/
    ASCII format[32];        /* format (i.e. academy) */
    U32   frame_position;    /* frame position in sequence */
    U32   sequence_len;      /* sequence length in frames */
    U32   held_count;        /* held count (1 = default) */
    R32   frame_rate;        /* frame rate of original in frames/sec */
    R32   shutter_angle;     /* shutter angle of camera in degrees */
    ASCII frame_id[32];      /* frame identification (i.e. keyframe) */
    ASCII slate_info[100];   /* slate information */
    U8    reserved[56];      /* reserved for future use (padding) */
} Motion_Picture_Film;

typedef struct _television_header
{
    U32 tim_code;            /* SMPTE time code */
    U32 userBits;            /* SMPTE user bits */
    U8  interlace;           /* interlace ( 0 = noninterlaced, 1 = 2:1 interlace*/
    U8  field_num;           /* field number */
    U8  video_signal;        /* video signal standard (table 4)*/
    U8  unused;              /* used for byte alignment only */
    R32 hor_sample_rate;     /* horizontal sampling rate in Hz */
    R32 ver_sample_rate;     /* vertical sampling rate in Hz */
    R32 frame_rate;          /* temporal sampling rate or frame rate in Hz */
    R32 time_offset;         /* time offset from sync to first pixel */
    R32 gamma;               /* gamma value */
    R32 black_level;         /* black level code value */
    R32 black_gain;          /* black gain */
    R32 break_point;         /* breakpoint */
    R32 white_level;         /* reference white level code value */
    R32 integration_times;   /* integration time(s) */
    U8  reserved[76];        /* reserved for future use (padding) */
} Television_Header;
"""

class DPX:

	def __init__(self,file):
		
		self.ImageOrientation = {}
		self.ImageOrientation[0]  = "left to right, top to bottom"
		self.ImageOrientation[1]  = "left to right, bottom to top"
		self.ImageOrientation[2]  = "right to left, top to bottom"
		self.ImageOrientation[3]  = "right to left, bottom to top"
		self.ImageOrientation[4]  = "top to bottom, left to right"
		self.ImageOrientation[5]  = "top to bottom, right to left"
		self.ImageOrientation[6]  = "bottom to top, left to right"
		self.ImageOrientation[7]  = "bottom to top, right to left"

		self.descriptor = {}
		self.descriptor[0]   = "User defined (or unspecified single component)"
		self.descriptor[1]   = "Red (R)"
		self.descriptor[2]   = "Green (G)"
		self.descriptor[3]   = "Blue (B)"
		self.descriptor[4]   = "Alpha (matte)"
		self.descriptor[5]   = ""
		self.descriptor[6]   = "Luminance (Y)"
		self.descriptor[7]   = "Chrominance (CB, CR, subsampled by two)"
		self.descriptor[8]   = "Depth (Z)"
		self.descriptor[9]   = "Composite video"
		self.descriptor[50]  = "R,G,B"
		self.descriptor[51]  = "R,G,B,alpha"
		self.descriptor[52]  = "Alpha, B, G, R"
		self.descriptor[100] = "CB, Y, CR, Y (4:2:2) -- based on SMPTE 125M"
		self.descriptor[101] = "CB, Y, a, CR, Y, a (4:2:2:4)"
		self.descriptor[102] = "CB, Y, CR (4:4:4)"
		self.descriptor[103] = "CB, Y, CR, a (4:4:4:4)"
		self.descriptor[150] = "User-defined 2 component element"
		self.descriptor[151] = "User-defined 3 component element"
		self.descriptor[152] = "User-defined 4 component element"
		self.descriptor[153] = "User-defined 5 component element"
		self.descriptor[154] = "User-defined 6 component element"
		self.descriptor[155] = "User-defined 7 component element"
		self.descriptor[156] = "User-defined 8 component element"


		# Initalize the structures
		self._file_information = "II8sIIIII100s24s100s200s200sI104s"
		self.__file_information = ["magic_num","offset","vers","file_size","ditto_key","gen_hdr_size","ind_hdr_size","user_data_size","file_name","create_time","creator","project","copyright","key","Reserved"]

		self._image_element = "IIfIfBBBBHHIII32s"
		self.__image_element = ( "data_sign","ref_low_data","ref_low_quantity","ref_high_data","ref_high_quantity","descriptor","transfer","colorimetric","bit_size","packing","encoding","data_offset","eol_padding","eo_image_padding","description" )
		self.__image_element1 = [ ("ie1-"+value) for value in self.__image_element]
		self.__image_element2 = [ ("ie2-"+value) for value in self.__image_element]
		self.__image_element3 = [ ("ie3-"+value) for value in self.__image_element]
		self.__image_element4 = [ ("ie4-"+value) for value in self.__image_element]
		self.__image_element5 = [ ("ie5-"+value) for value in self.__image_element]
		self.__image_element6 = [ ("ie6-"+value) for value in self.__image_element]
		self.__image_element7 = [ ("ie7-"+value) for value in self.__image_element]
		self.__image_element8 = [ ("ie8-"+value) for value in self.__image_element]
		self._image_information = "HHII%s%s%s%s%s%s%s%s52s" % (
																													self._image_element,
																													self._image_element,
																													self._image_element,
																													self._image_element,
																													self._image_element,
																													self._image_element,
																													self._image_element,
																													self._image_element )
		self.__image_information = [ "orientation","element_number","pixels_per_line","lines_per_image_ele"]
		self.__image_information.extend(self.__image_element1)
		self.__image_information.extend(self.__image_element2)
		self.__image_information.extend(self.__image_element3)
		self.__image_information.extend(self.__image_element4)
		self.__image_information.extend(self.__image_element5)
		self.__image_information.extend(self.__image_element6)
		self.__image_information.extend(self.__image_element7)
		self.__image_information.extend(self.__image_element8)
		self.__image_information.extend(['Reserved'])

		self._image_orientation = "IIffII100s24s32s32sHHHHII28s"
		self.__image_orientation = [ "x_offset","y_offset","x_center","y_center","x_orig_size","y_orig_size","file_name","creation_time","input_dev","input_serial","border-XL","border-XR","border-YT","border-YB","pixel_aspect-h","pixel_aspect-v","Reserved" ]

		self._motion_picture_film_header = "2s2s2s6s4s32sIIIff32s100s56s"
		self.__motion_picture_film_header = [ "film_mfg_id","film_type","offset","prefix","count","format","frame_position","sequence_len","held_count","frame_rate","shutter_angle","frame_id","slate_info","Reserved"]

		self._television_header = "IIBBBBffffffffff76s"
		self.__television_header = [ "tim_code","userBits","interlace","field_num","video_signal","unused","hor_sample_rate","ver_sample_rate","frame_rate","time_offset","gamma","black_level","black_gain","break_point","white_level","integration_times","Reserved" ]
		self.file_information = None
		self.image_information = None
		self.image_orientation = None
		self.motion_picture_film_header = None

		self.file = file
		self.valid = False
		self.raw_string = False
		self.full_headers_lookup = []
		self.full_headers_lookup.extend(self.__file_information)
		self.full_headers_lookup.extend(self.__image_information)
		self.full_headers_lookup.extend(self.__image_orientation)
		self.full_headers_lookup.extend(self.__motion_picture_film_header)
		self.full_headers_lookup.extend(self.__television_header)
		self._full_headers  = self._file_information
		self._full_headers += self._image_information
		self._full_headers += self._image_orientation
		self._full_headers += self._motion_picture_film_header
		self._full_headers += self._television_header
		if not self.file:
			return 

		# open file and load the the headers.
		if not os.path.isfile(file):
			return 
		try:
			fp = open(self.file,"r")
		except IOError,message:
			print message
			return

		# figure out endieness from the first 4 bytes.
		byteorder = fp.read(4)
		if byteorder == "SDPX":
			self.bigendit()
		elif byteorder == "XPDS":
			self.smallendit()

		else:
			return 
		fp.seek(0)
		# load the struct up with data.
		file_information = fp.read( struct.calcsize(self._file_information) )
		self.file_information = struct.unpack( self._file_information, file_information )
		image_information = fp.read( struct.calcsize(self._image_information) )
		self.image_information = struct.unpack( self._image_information, image_information )
		image_orientation = fp.read( struct.calcsize(self._image_orientation) )
		self.image_orientation = struct.unpack( self._image_orientation, image_orientation )
		motion_picture_film_header = fp.read( struct.calcsize(self._motion_picture_film_header) )
		self.motion_picture_film_header = struct.unpack( self._motion_picture_film_header, motion_picture_film_header )
		television_header = fp.read( struct.calcsize(self._television_header) )
		self.television_header = struct.unpack( self._television_header, television_header )
		fp.close()
		# create a list with the whole header content,.
		self.full_headers = []
		self.full_headers.extend(self.file_information)
		self.full_headers.extend(self.image_information)
		self.full_headers.extend(self.image_orientation)
		self.full_headers.extend(self.motion_picture_film_header)
		self.full_headers.extend(self.television_header)
		return 

	# Dictionnary emulations code:
	def __len__(self): return len(self.full_headers)

	def __getitem__(self, key): 
		try:
			if type(self.full_headers[self.full_headers_lookup.index(key)]) is types.StringType:
				return self.clean_string(self.full_headers[self.full_headers_lookup.index(key)])
			else:
				return self.full_headers[self.full_headers_lookup.index(key)]
		except:
			raise KeyError, key

	def __setitem__(self, key, item): 
		try:
			index = self.full_headers_lookup.index(key)
		except:
			raise KeyError, key
		try:
			if type(self.full_headers[index]) is types.IntType:
				self.full_headers[index]= int(item)
			elif type(self.full_headers[index]) is types.LongType:
				self.full_headers[index]= long(item)
			elif type(self.full_headers[index]) is types.FloatType:
				self.full_headers[index]= float(item)
			elif type(self.full_headers[index]) is types.StringType:
				self.full_headers[index]= str(item)
			else:
				raise KeyError, "add case for %s" % type(item)
		except Exception, inst:
			print Exception, inst

	def __contains__(self, key): return key in self.full_headers_lookup

	def keys(self):
		""" returns the keys in the dictionnary """
		return self.full_headers_lookup

	def items(self):
		""" returns the items in the dictionnary """
		ret = []
		for i in range(0,len(self.full_headers_lookup)):
			ret.append((self.full_headers_lookup[i],self.full_headers[i]))
		return ret

	def values(self):
		""" returns the values in the dictionnary """
		return self.full_headers.values()

	def has_key(self, key):
		""" is a key in the dictionnary """
		return self.full_headers_lookup.count(key)
	
	def save(self):
		if not self.valid:
			raise "Not a DPX"
		full_headers = struct.pack(self._full_headers, *self.full_headers)
		fd=os.open(self.file,os.O_WRONLY)
		try:
			os.lseek(fd,0,os.SEEK_SET)
			wr = os.write(fd,full_headers)
		finally:
			os.close(fd)
	

	# hearder replacement.
	def hearder(self):
		for i in range(0,len(self.full_headers_lookup)):
			if self.full_headers_lookup[i] == "Reserved":
				pass
			elif self.full_headers_lookup[i] == "key":
				if self.full_headers[i] == 2**32-1:
					print "key: unencrypted"
				else:
					print "%s: %s" % ( self.full_headers_lookup[i], self.full_headers[i])
			elif self.full_headers_lookup[i] == "orientation":
				print "%s: %s" % ( self.full_headers_lookup[i],
												self.ImageOrientation[ self.full_headers[i] ] )
			elif self.full_headers_lookup[i][4:] == "descriptor":
				try:
					print "%s: %s" % ( self.full_headers_lookup[i], 
												self.descriptor[ self.full_headers[i] ] )
				except:
					print "%s: %s" % ( self.full_headers_lookup[i], "unknown" )
			else:
				if self.full_headers_lookup[i] == 2**32-1:
					print "%s: undefined" % ( self.full_headers_lookup[i] )
				elif type (self.full_headers[i] ) is types.StringType: 
					print "%s: %s" % ( self.full_headers_lookup[i],self.clean_string(self.full_headers[i])  )
				else:
					print "%s: %s" % ( self.full_headers_lookup[i],self.full_headers[i] )
		return 

	def bigendit(self):
		if self._file_information[0] == "<" or self._file_information[0]== ">":
			self._file_information = ">" + self._file_information[1:]
			self._image_information = ">" + self._image_information[1:]
			self._image_orientation = ">" + self._image_orientation[1:]
			self._motion_picture_film_header = ">" + self._motion_picture_film_header[1:]
			self._television_header = ">" + self._television_header[1:]
			self._full_headers = ">" + self._full_headers[1:]
		else:
			self._file_information = ">" + self._file_information
			self._image_information = ">" + self._image_information
			self._image_orientation = ">" + self._image_orientation
			self._motion_picture_film_header = ">" + self._motion_picture_film_header
			self._television_header = ">" + self._television_header
			self._full_headers = ">" + self._full_headers
		self.valid = True
		self.endianess = 'big-endian'

	def smallendit(self):
		if self._file_information == "<" or self._file_information[0]== ">":
			self._file_information = "<" +  self._file_information[1:]
			self._image_information = "<" + self._image_information[1:]
			self._image_orientation = "<" + self._image_orientation[1:]
			self._motion_picture_film_header = "<" + self._image_orientation[1:]
			self._television_header = "<"  + self._television_header[1:]
			self._full_headers = "<" + self._full_headers[1:]
		else:	
			self._file_information = "<" + self._file_information
			self._image_information = "<" + self._image_information
			self._image_orientation = "<" + self._image_orientation
			self._motion_picture_film_header = "<" + self._motion_picture_film_header
			self._television_header = "<" + self._television_header
			self._full_headers = "<" + self._full_headers
		self.valid = True
		self.endianess = 'little-endian'

	def clean_string(self,s):
		""" removes un-encodable char from a string 
				I know it's ugly but it works            """
		if self.raw_string:
			return s
		else:
			return string.translate(s,string.maketrans("",""),"'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff")


if __name__ == '__main__':


	def usage():
		print "Usage: dpxhearder [OPTION]... FILE"
		print "display or modify dpx header information"
		print ""
		print "  -k, --key                 select which keys to show"
		print "  -s, --set                 set a header value key=value"
		print "  -g, --get-keys            get the list of valid keys"
		print "  -r, --raw                 don't sanitize the string values"
		print "      --shakeit             Fix the dpx for shake"

	import pwd
#	if ( 3001 in os.getgroups() ) or ( 7001 in os.getgroups() ) or ( os.getuid == 0 ):
#		pass
#	else:
#		print "you are not authorized to run this"
#		sys.exit(1)

	try:
		opts, args = getopt.getopt(sys.argv[1:],"hgk:s:r",["help","get-keys","key=","set=","shakeit","raw","big","small"])
	except:
		usage()
		sys.exit(1)
	hearder = True
	raw = False
	keys = []
	sets = []
	shakeit = False
	endianness = None
	for o,a in opts:
		if o in ("-h","--help"):
			usage()
		if o in ("-g","--get-keys"):
			dpx = DPX(None)
			for key in dpx.keys():
				print key, 
			sys.exit(0)
		if o in ("-k","--key"):
			keys.append(a)
			hearder = False
		if o == "-s" or o == "--set":
			hearder = False
			sets.append(a)
		if o == "-r" or o == "--raw":
			raw = True
		if o == "--big":
			endianness = "big"
		if o == "--small":
			endianness = "small"
		if o == "--shakeit":
			hearder = False
			shakeit = True
	if args == []:
		usage()
		sys.exit(1)
	for file in args:
		print "-"*40
		dpx = DPX(file)
		dpx.raw_string = raw
		# Is this a valid DPX ?
		if dpx.valid:
			print file

			# do we have setting to do ?
			if sets != []:
				for set in sets:
					try:
						key,value = set.split("=")
						if key in dpx.keys():
							dpx[key] = value
							print "%s: %s" % ( key, dpx[key] )
						else:
							print "%s doesn't exist" % key
					except:
						pass
					dpx.save()
			if endianness:
				if endianness == "big":
					dpx.bigendit()
					dpx.save()
				if endianness == "small":
					dpx.smallendit()
					dpx.save()

			# do we only want show specific keys ?
			if keys != []:
				for key in keys:
					if key in dpx.keys():
						print "%s: %s" % ( key, dpx[key] )
					else:
						print "%s doesn't exist" % key

			# fix some dpx
			if shakeit:
				if dpx['offset'] == 0 :
					dpx['ie1-data_offset']=dpx['offset']
					dpx.save()

			# Print all the headers
			if hearder:
				dpx.hearder()

		else:
			print "%s is Not a Valid DPX" % file
