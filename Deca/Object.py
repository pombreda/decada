# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Object
# Purpose:     A generic DECA object
#
# Author:      Stinger
#
# Created:     19.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from collections import OrderedDict
import os
import uuid
import Deca
from persistent import Persistent
from persistent.mapping import PersistentMapping
import gettext

_ = gettext.gettext

__author__ = 'Stinger'
LOCAL = 0
BASE = 1
BOTH = 2

class DecaTemplate(Persistent):
	def __init__(self, id = None):
		if id is not None:
			self.ID = id
		else:
			self.ID = uuid.uuid4()
		self.Name = ""
		self.Attributes = PersistentMapping()
		self.TitleAttr = None
		self.Graphics = None

	def copy(self, newID):
		obj = DecaTemplate(newID)
		obj.Name = self.Name
		obj.TitleAttr = self.TitleAttr
		obj.Attributes = self.Attributes.copy()
		obj.Graphics = self.Graphics
		return obj

class DecaShape(Persistent):
	def __init__(self, name):
		self.ID = name

	def copy(self, name):
		obj = DecaShape(name)
		for k in self.__dict__.keys():
			obj.__setattr__(k, self.__getattribute__(k))
		return obj

	def GetRegionName(self):
		"""For compatibility with olg.Shape usage"""
		return self.ID

class DecaObject(Persistent):
	"""A generic DECA object"""
	def __init__(self, id = None):
		if id is not None:
			self.ID = id
		else:
			self.ID = uuid.uuid4()
		self.TemplateName = ""
		self.Attributes = PersistentMapping()
		self.TitleAttr = None
		self.Graphics = None
		self.IsReflection = False
		self.Tag = None

	def copy(self, newID):
		obj = DecaObject(newID)
		obj.TemplateName = self.TemplateName
		obj.TitleAttr = self.TitleAttr
		for k,v in self.Attributes.items() :
			obj.Attributes[k] = v
		obj.Graphics = self.Graphics
		obj.IsReflection = self.IsReflection
		obj.Tag = self.Tag
		return obj

	def GetTitle(self):
		"""Returns the title of the object. If the Title Attribute defined, it's value will be returned.
		Else if Tag defined, it's value will be returned. Else the object's ID will be returned. """
		if self.TitleAttr is not None:
			return self.Attributes[self.TitleAttr]
		if self.Tag is not None and str(self.Tag) != '':
			return str(self.Tag)
		return str(self.ID)

	def SetAttr(self, name, value, location=LOCAL):
		"""Sets the attribute value in desired location.

		**Note:** if the object isn't the reflect, attribute will be stored locally"""
		if location == LOCAL :
			self.Attributes[name] = value
		# todo: set attribute to the base object if we are reflection

	def GetAttr(self, name, default=None, priority=LOCAL):
		"""Gets the attribute value. For the reflects the priority may points that the base value must be given.
		If value absent in desired location other locations will be scanned. Finnaly, the default value will be returned"""
		result = default
		if priority == LOCAL :
			result = self.Attributes.get(name, default)
		else:
			# todo: read base object's property if we are reflection
			pass
		return result

	def GetShape(self):
		# todo: get shape description. Is it necessary?
		return 

	def GetPropList(self, holder = None) :
		self.propsGrid = holder
		props = OrderedDict([
			('Identity', self.ID),
			('Template', self.TemplateName),
			('Title Attribute', self.TitleAttr),
			('Is Reflection', self.IsReflection),
		])
		attrs = OrderedDict([])
		for k,v in self.Attributes.items():
			attrs.update([(k, v)])
		result = OrderedDict([
			(_("Object's properties"), props),
			(_("Local object's attributes"), attrs)
		])
		return result

	def ReflectTo(self, dstLayer):
		if not isinstance(dstLayer, Deca.Layer):
			dstLayer = Deca.world.GetLayer(str(dstLayer))
		if not self.ID in dstLayer.storage.objects.keys():
			nwo = self.copy(self.ID)
			nwo.IsReflection = True
			dstLayer.AddObject(nwo)
			return nwo
		return None

	def GetEngines(self):
		def genList(base, dirlist):
			res = []
			for ent in dirlist:
				if os.path.isdir(os.path.join(base, ent)):
					# process subdir
					nb = os.path.join(base, ent)
					res.append( (ent, genList(nb, os.listdir(nb))) )
				else:
					ft = os.path.splitext(ent)
					if ft[1].lower() == '.py':
						res.append(ft[0])
			return res
		# main function
		pl = []
		if self.TemplateName and self.TemplateName != '' :
			epath = os.path.join(Deca.world.EnginesPath, self.TemplateName)
			if os.path.isdir(epath):
				pl = genList(epath, os.listdir(epath))
			# if Object's engines
		# if template given
		return pl

	def ExecuteEngine(self, name, layer, shape = None, dict = None):
		item = os.path.join(Deca.world.EnginesPath, self.TemplateName, name + '.py')
		fl = None
		if not dict:
			dict = globals()
		try:
			fl = open(item, 'r')
			dict['ActiveDecaLayer'] = layer
			if not shape:
				shape = layer.GetShape(self.ID)
			dict['ActiveShape'] = shape
			exec fl in dict
		finally:
			if fl : fl.close()
