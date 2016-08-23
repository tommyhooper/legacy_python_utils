#!/usr/bin/env python


import logging
import logging.config
logging.config.fileConfig('daemon.ini')
log = logging.getLogger('a52sd')

#formatter = logging.Formatter('PYTHON LOGGING: %(levelname)s: %(message)s')
#
#s = handlers.SysLogHandler(address='/dev/log')
#s.setFormatter(formatter)
#log.addHandler(s)
#
#c = logging.StreamHandler()
#c_formatter = logging.Formatter('%(asctime)s PYTHON LOGGING: %(levelname)s: %(message)s')
#c.setFormatter(c_formatter)
#log.addHandler(c)
#
#l = logging.FileHandler('/var/pylog.log')
#l.setFormatter(c_formatter)
#log.addHandler(l)
#

log.info('test info')
log.warning('test warning')
log.error('test error')
