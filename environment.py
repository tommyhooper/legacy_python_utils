#!/usr/bin/python

import os

# mapping from human readable name to machine usable dir name
#CONTEXT_OPTIONS = ('test', 'local', 'dev', 'live')
CONTEXT_OPTIONS = ('dev', 'live')
CURRENT_CONTEXT = None

def set_context(context):
    global CURRENT_CONTEXT
    if context in CONTEXT_OPTIONS:
        CURRENT_CONTEXT = context
    else:
        raise Exception("Context does not exists %s" % context)
    
def get_context():
	global CURRENT_CONTEXT
	if CURRENT_CONTEXT != None:
		return CURRENT_CONTEXT
	else:
		my_location =  os.path.realpath(__file__)
		if my_location.find('lib') >= 0:
			return 'live'
		elif my_location.find('dev') >= 0:
			return 'dev'
	return CURRENT_CONTEXT
    
def db_settings_for_context(connection_name, context=None):
    """
    Returns a list of databases and their settings for a given context
    """
    from A52 import settings
    if not context:
        context = get_context()
   
    try:
        return settings.DB_PROPERTIES[context][connection_name]
    except Exception:
        print "%s is not specified in settings" % (connection_name)


if __name__ == "__main__":
    print get_context()
