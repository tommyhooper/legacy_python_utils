import datetime
import string
import re
try: from hashlib import md5
except ImportError: from md5 import md5

def generate_random_string(length=8):
    """
    Remove a random string up to 32 characters in length
    """
    h = md5()
    h.update(str(datetime.datetime.now()))
    return h.hexdigest()[0:length]

def file_safe_name(str):
    space_pattern = re.compile('\s+')
    str = space_pattern.sub('_', str)
    
    non_alpha_pattern = re.compile('\W')
    str = non_alpha_pattern.sub('', str)
    return str.lower()

def normalize(str):
    """
    Remove all non-alpha numeric characters for easier comparison
    """
    non_alpha_pattern = re.compile('[^A-Za-z0-9]')
    str = non_alpha_pattern.sub('', str)
    return str.lower()

def clean_string(bad_text):
	## convert the text
	# trim before and after
	#wash = string.lower(bad_text).strip()
	wash = bad_text.strip()
	# change - & " " to _
	#soap = re.sub('([\ -])','_',wash)
	soap = re.sub('([\ ])','_',wash)
	# strip out strange characters
	rinse = re.sub('[^A-za-z0-9-_\.<>%]','',soap)
	# squeeze reapeting "_"'s
	spin = re.sub('[_]+','_',rinse)
	return spin

def extract_numbers(text):
	try:
		return int(''.join([d for d in text if d.isdigit()]).lstrip('0'))
	except:
		return None



