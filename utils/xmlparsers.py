#!/usr/bin/python

import sys
# Different code path for different version of python 2.[45]
if sys.version_info[1] == 3:
	from elementtree import ElementTree
elif sys.version_info[1] == 4:
	import cElementTree as ElementTree
elif sys.version_info[1] == 5:
	import xml.etree.cElementTree as ElementTree

class XmlListConfig(list):


	def __init__(self, aList):
		for element in aList:
			if element:
				if len(element) == 1 or element[0].tag != element[1].tag:
					self.append(XmlDictConfig(element))
				elif element[0].tag == element[1].tag:
					self.append(XmlListConfig(element))
			elif element.text:
				text = element.text.strip()
				if text:
					self.append(text)

class XmlDictConfig(dict):


	def __init__(self, parent_element):
		if parent_element.items():
			self.update({'attr':dict(parent_element.items())})
		for element in parent_element:
			if element:
				# treat like dict - we assume that if the first two tags
				# in a series are different, then they are all different.
				if len(element) == 1 or element[0].tag != element[1].tag:
					aDict = XmlDictConfig(element)
				# treat like list - we assume that if the first two tags
				# in a series are the same, then the rest are the same.
				else:
					# here, we put the list in dictionary; the key is the
					# tag name the list elements all share in common, and
					# the value is the list itself
					aDict = {element[0].tag: XmlListConfig(element)}
				# if the tag has attributes, add those to the dict
				if element.items():
					aDict.update(dict(element.items()))
				self.update({element.tag: aDict})
			# this assumes that if you've got an attribute in a tag,
			# you won't be having any text. This may or may not be a
			# good idea -- time will tell. It works for the way we are
			# currently doing XML configuration files...
			elif element.items():
				self.update({element.tag: dict(element.items())})
			# finally, if there are no child tags and no attributes, extract
			# the text
			else:
				self.update({element.tag: element.text})

def xml_to_dict(xml):
	return XmlDictConfig(ElementTree.XML(xml))


