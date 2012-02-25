# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Layer
# Purpose:     The DECA Layer and Repository objects
#
# Author:      Stinger
#
# Created:     21.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from collections import OrderedDict
import os
from persistent import Persistent
from random import randint
import uuid
from persistent.mapping import PersistentMapping
import Deca
from Deca import Object, Utility
from Deca.Link import DecaLink
from Deca.Object import DecaTemplate, DecaObject, DecaShape
import gettext
_ = gettext.gettext

__author__ = 'Stinger'

class DecaLayerStorage(Persistent):
	def __init__(self):
		Persistent.__init__(self)
		self.objects = PersistentMapping()
		self.links = PersistentMapping()
		self.graph_data = PersistentMapping()
		self.Tag = None

class DecaRepoStorage(Persistent):
	def __init__(self):
		Persistent.__init__(self)
		self.objects = PersistentMapping()
		self.templates = PersistentMapping()
		self.shapes = PersistentMapping()
		self.Tag = None

class DecaLayer:
	def __init__(self, world, name):
		self.world = world
		self.propsGrid = None
		self.name = name
		self.storage = world.roots[name]

	def GetPropList(self, holder = None) :
		self.propsGrid = holder
		result = OrderedDict([
			(_("Layer %s") % self.name,  OrderedDict([
				(_("Objects"), len(self.storage.objects)),
				(_("Links"), len(self.storage.links))
			]))
		])
		return result

	def CreateObject(self, sample=None):
		obj = DecaObject()
		if sample is not None:
			if isinstance(sample, DecaTemplate):
				#fill from template
				obj.TemplateName = sample.Name
				obj.TitleAttr = sample.TitleAttr
				for k,v in sample.Attributes.items() :
					obj.Attributes[k] = v
				obj.Graphics = sample.Graphics
			if isinstance(sample, DecaObject):
				#fill from another object
				obj.TemplateName = sample.storage.TemplateName
				for k,v in sample.storage.Attributes.items() :
					obj.Attributes[k] = v
				obj.TitleAttr = sample.TitleAttr
				obj.Graphics = sample.storage.Graphics
				obj.IsReflection = sample.storage.IsReflection
				obj.Tag = sample.storage.Tag
		else:
			#fill from default template
			tpl = self.storage.templates[DecaRepo.ID_DefaultTemplate]
			obj.TemplateName = tpl.Name
			obj.TitleAttr = tpl.TitleAttr
			for k,v in tpl.Attributes.items() :
				obj.Attributes[k] = v
			obj.Graphics = tpl.Graphics
		self.storage.objects[obj.ID] = obj
		return obj

	def AddObject(self, obj):
		if obj.ID not in self.storage.objects.keys():
			self.storage.objects[obj.ID] = obj
		return self

	def GetObject(self, oid):
		if not isinstance(oid, uuid.UUID) :
			oid = uuid.UUID(str(oid))
		return self.storage.objects.get(oid)

	def GetObjects(self, filter=None):
		return Utility.Filter(filter, self.storage.objects).values()

	def GetObjectsIDs(self, filter=None):
		return Utility.Filter(filter, self.storage.objects).keys()

	def RemoveObject(self, obj):
		# todo: remove object from layer
		if isinstance(obj, DecaObject):
			oid = obj.ID
		elif isinstance(obj, uuid.UUID):
			oid = obj
		else:
			oid = uuid.UUID(str(obj))
		self.RemoveObjectLinks(oid)
		del self.storage.objects[oid]
		del self.storage.graph_data[oid]
		return oid

	def CreateLink(self, obj_from, obj_to, direct=False):
		if isinstance(obj_from, DecaObject):
			obj_from = obj_from.ID
		if isinstance(obj_to, DecaObject):
			obj_to = obj_to.ID
		lid = DecaLink.BuildID(obj_from, obj_to)
		if lid not in self.storage.links:
			lnk = DecaLink(obj_from, obj_to, direct)
			self.storage.links[lnk.ID] = lnk
			return lnk
		else:
			return self.storage.links[lid]

	def AddLink(self, lnk):
		if lnk.ID not in self.storage.links.keys():
			self.storage.links[lnk.ID] = lnk
		return self

	def GetLinks(self, filter=None):
		return Utility.Filter(filter, self.storage.links.values())

	def RemoveLink(self, lnk):
		"""Removes given link object(s) from the layer"""
		# remove link from layer
		if isinstance(lnk, DecaLink):
			lid = lnk.ID
		else:
			lid = int(lnk)
		del self.storage.links[lid]
		del self.storage.graph_data[lid]
		return lid

	def RemoveObjectLinks(self, obj):
		"""Removes links for the given object.
		Remove links that starts or finish at the object.

		:param obj: - Object ID or Object instance to remove links
		"""
		# todo: remove object's links from layer
		oid = obj
		if isinstance(obj, DecaObject):
			oid = obj.ID
		elif isinstance(obj, uuid.UUID):
			oid = obj
		else:
			oid = uuid.UUID(str(obj))
		lnks = self.GetLinks(lambda lnk: lnk.StartObject == oid or lnk.FinishObject == oid)
		for l in lnks:
			self.RemoveLink(l)
		pass

	def ReflectTo(self, dstLayer, objFilter, lnkFilter):
		if not isinstance(dstLayer, Deca.Layer):
			dstLayer = Deca.world.GetLayer(str(dstLayer))
		olist = self.GetObjects(objFilter)
		oids = [x.ID for x in olist]
		llist = self.GetLinks(lambda link: link.StartObject in oids and link.FinishObject in oids)
		llist = Utility.Filter(lnkFilter, llist)
		# copy data to rlayer
		for obj in olist:
			if obj: obj.ReflectTo(dstLayer)
		for lnk in llist:
			dstLayer.AddLink(lnk)
		pass

	def Clear(self):
		self.storage.objects = PersistentMapping()
		self.storage.links = PersistentMapping()
		self.storage.graph_data = PersistentMapping()

	def ClearShapes(self):
		vm = op = None
		if '@view' in self.storage.graph_data.keys():
			vm = self.storage.graph_data['@view']
		if '@opts' in self.storage.graph_data.keys():
			op = self.storage.graph_data['@opts']
		self.storage.graph_data.clear()
		if vm:
			self.storage.graph_data['@view'] = vm
		if op:
			self.storage.graph_data['@opts'] = op

	def GetShape(self, shp_id):
		"""Returns shape for the given identifier.
		If such shape not in the shapes list, the dummy shape returned
		"""
		if not shp_id in self.storage.graph_data.keys():
			shape = DecaShape(shp_id)
			shape.Tag = 'unknown'
			return shape
		return self.storage.graph_data[shp_id]

	def SetViewOption(self, name, value):
		if '@opts' not in self.storage.graph_data.keys():
			shi = DecaShape('@opts')
			shi.Tag = '@opts'
			self.storage.graph_data['@opts'] = shi
		self.storage.graph_data['@opts'].__setattr__(name, value)

	def GetViewOption(self, name, defvalue):
		if '@opts' not in self.storage.graph_data.keys():
			shi = DecaShape('@opts')
			shi.Tag = '@opts'
			self.storage.graph_data['@opts'] = shi
			return defvalue
		if hasattr(self.storage.graph_data['@opts'], name):
			return getattr(self.storage.graph_data['@opts'], name, defvalue)
		return defvalue

	def AddObjectShape(self, obj, xpos = None, ypos = None, shapeTmpl = None):
		"""Add shape information to the layer. If coordinates are None, random position
		will be selected. ShapeTmpl can be given to describe shape's paramenters

		:param obj: :class:`Deca.Object` to add shape
		:param xpos: X coordinate of the shape's center
		:param ypos: Y coordinate of the shape's center
		:param shapeTmpl: :class:`Deca.Shape` describes the drawing parameters
		:returns: :class:`Deca.Shape` of the created shape
		"""
		shape = None
		if isinstance(obj, Deca.Object):
			if not xpos:
				if shapeTmpl :
					xpos = shapeTmpl.xpos
				else :
					xpos = randint(0, 500)
			if not ypos:
				if shapeTmpl :
					ypos = shapeTmpl.ypos
				else :
					ypos = randint(0, 500)
			if obj.ID in self.storage.graph_data.keys():
				# remove current shape
				xpos = self.storage.graph_data[obj.ID].xpos
				ypos = self.storage.graph_data[obj.ID].ypos
				#self.diagram.RemoveShape(self.shapes[obj.ID])
			# create shape info
			if shapeTmpl :
				shape = shapeTmpl.copy(shapeTmpl.ID)
			else:
				shape = DecaShape(obj.ID)
			shape.Tag = 'object'
			shape.xpos = xpos
			shape.ypos = ypos
			shape.label = obj.GetTitle()
			if not shapeTmpl:
				shape.width = self.GetViewOption('defaultShapeWidth', 100)
				shape.height = self.GetViewOption('defaultShapeHeight', 50)
				shape.pen = ()
				shape.brush = ()
			self.storage.graph_data[obj.ID] = shape
			self.Modified = True
		return shape

	def AddLinkShape(self, lnk, shapeTmpl = None):
		"""Add link-shape information to the layer.
		ShapeTmpl can be given to describe shape's paramenters

		:param lnk: :class:`Deca.Link` to add shape
		:param shapeTmpl: :class:`Deca.Shape` describes the drawing parameters
		:returns: :class:`Deca.Shape` of the created shape
		"""
		line = None
		fromShape = self.storage.graph_data.get(lnk.StartObject, None)
		toShape = self.storage.graph_data.get(lnk.FinishObject, None)
		if fromShape and toShape:
			if shapeTmpl :
				line = shapeTmpl.copy(shapeTmpl.ID)
			else:
				line = DecaShape(lnk.ID)
			line.Tag = 'link'
			line.start = lnk.StartObject
			line.finish = lnk.FinishObject
			line.direct = lnk.Directional
			line.label = getattr(lnk, 'Title', '')
			if not shapeTmpl:
				line.pen = ()
				line.brush = ()
			if not hasattr(line, 'ControlPoints'):
				line.ControlPoints = self.GetViewOption('defaultLineCP', 2)
				line.CPArray = []
			if not hasattr(line, 'spline'):
				line.spline = self.GetViewOption('defaultLineSpline', False)
			self.storage.graph_data[lnk.ID] = line
			self.Modified = True
		# link added
		return line

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
					if ft[1].lower() == '.py' and not ft[0].startswith('_'):
						res.append(ft[0])
			return res
		# main function
		pl = []
		epath = os.path.join(Deca.world.EnginesPath, 'layer')
		if os.path.isdir(epath):
			pl = genList(epath, os.listdir(epath))
		return pl


	def ExecuteEngine(self, name, dict = None):
		item = os.path.join(Deca.world.EnginesPath, 'layer', name + '.py')
		fl = None
		if not dict:
			dict = globals()
		try:
			fl = open(item, 'r')
			dict['ActiveDecaLayer'] = self
			exec fl in dict
		finally:
			if fl : fl.close()

	@property
	def Modified(self):	return self.storage._p_changed
	
	@Modified.setter
	def Modified(self, value):	self.storage._p_changed = value

class DecaRepo:
	ID_DefaultTemplate = uuid.uuid3(uuid.NAMESPACE_DNS, 'Deca.World.Repository.default')
	
	def __init__(self, world, name):
		self.world = world
		self.propsGrid = None
		self.storage = world.roots[name]
		if self.ID_DefaultTemplate not in self.storage.templates.keys() :
			tpl = DecaTemplate(self.ID_DefaultTemplate)
			tpl.Name = _('Default')
			self.storage.templates[tpl.ID] = tpl
		self.nameindex = {}
		self.LazyReindex()

	def AddTemplate(self, name, copy = None):
		try:
			code = 'Deca.World.Repository.%s' % name
			code = code.encode('ascii')
			id = uuid.uuid3(uuid.NAMESPACE_DNS, code)
		except Exception:
			id = uuid.uuid4()
		if id in self.storage.templates.keys():
			return None
		if copy is not None and isinstance(copy, DecaTemplate):
			tpl = copy.copy(id)
		else:
			tpl = Object.DecaTemplate(id)
		tpl.Name = name
		self.storage.templates[tpl.ID] = tpl
		return tpl

	def GetTemplate(self, id):
		if not isinstance(id, uuid.UUID) :
			id = uuid.UUID(str(id))
		if id in self.storage.templates.keys():
			return self.storage.templates[id]
		return None

	def LazyReindex(self):
		self.nameindex.clear()
		for tpl in self.storage.templates.values():
			self.nameindex[tpl.Name] = tpl

	def GetTemplateByName(self, name):
		if name in self.nameindex.keys():
			return self.nameindex[name]
		return None

	def GetTemplatesIDs(self, filter=None):
		return Utility.Filter(filter, self.storage.templates).keys()

	def GetTemplatesNames(self, filter=None):
		return [x.Name for x in Utility.Filter(filter, self.storage.templates).values()]

	def GetTemplates(self, filter=None):
		return [x for x in Utility.Filter(filter, self.storage.templates).values()]

	def RemoveTemplate(self, tid):
		if hasattr(tid, '__iter__') :
			for i in tid:
				if not isinstance(i, uuid.UUID) :
					i = uuid.UUID(str(i))
				del self.storage.templates[i]
		else:
			if not isinstance(tid, uuid.UUID) :
				tid = uuid.UUID(str(tid))
			del self.storage.templates[tid]

	def AddObject(self, sample=None):
		obj = DecaObject()
		if sample is not None:
			if isinstance(sample, DecaTemplate):
				#fill from template
				obj.TemplateName = sample.Name
				for k,v in sample.Attributes.items() :
					obj.Attributes[k] = v
				obj.Graphics = sample.Graphics
			if isinstance(sample, DecaObject):
				#fill from another object
				obj.TemplateName = sample.storage.TemplateName
				for k,v in sample.storage.Attributes.items() :
					obj.Attributes[k] = v
				obj.Graphics = sample.storage.Graphics
				obj.IsReflection = sample.storage.IsReflection
				obj.Tag = sample.storage.Tag
		else:
			#fill from default template
			tpl = self.storage.templates[self.ID_DefaultTemplate]
			obj.TemplateName = tpl.Name
			for k,v in tpl.Attributes.items() :
				obj.Attributes[k] = v
			obj.Graphics = tpl.Graphics
		self.storage.objects[obj.ID] = obj
		return obj

	def GetObject(self, oid):
		if not isinstance(oid, uuid.UUID) :
			oid = uuid.UUID(str(oid))
		return self.storage.objects.get(oid)

	def GetObjects(self, filter=None):
		return Utility.Filter(filter, self.storage.objects).values()

	def GetObjectsIDs(self, filter=None):
		return Utility.Filter(filter, self.storage.objects).keys()

	def RemoveObject(self, tid):
		if hasattr(tid, '__iter__') :
			for i in tid:
				if not isinstance(i, uuid.UUID) :
					i = uuid.UUID(str(id))
				self.storage.objects.remove(i)
		else:
			if not isinstance(tid, uuid.UUID) :
				tid = uuid.UUID(str(id))
			self.storage.objects.remove(tid)

	def GetPropList(self, holder = None) :
		self.propsGrid = holder
		result = OrderedDict([
			(_("Repository"),  OrderedDict([
				(_("Templates"), len(self.storage.templates)),
				(_("Objects"), len(self.storage.objects)),
				(_("Shapes"), len(Deca.world.GetShapes()))
			]))
		])
		return result
