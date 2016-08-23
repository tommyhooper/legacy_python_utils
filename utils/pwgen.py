#!/usr/bin/python
import commands
def generatePassword(len=8):
  """ Return a pronounceable passwords yet secure """
  return commands.getoutput("pwgen %d 1" % len ).strip()
