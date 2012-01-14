# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ShapeBase
# Purpose:     Description for the ShapeBase
#
# Author:      aabramov
#
# Created:     25.11.11
# Copyright:   (c) aabramov 2011
# Licence:     Private
#-------------------------------------------------------------------------------
from collections import OrderedDict
import Deca
import gettext
_ = gettext.gettext

__author__ = 'aabramov'

###########################################################################
## Class ObjectShape - graphical object representation
###########################################################################
class ObjectShapeBase :
	def __init__(self):
		self.object = None
		self._pen = None
		self._brush = None
		self._textColourName = None
		self._width = None
		self._height = None
		self.propsGrid = None

	def Update(self):
		if self.propsGrid:
			self.propsGrid.UpdateGrid()
		pass

	def GetPropList(self, holder = None) :
		self.propsGrid = holder
		result = None
		if self.object:
			result = self.object.GetPropList()
			if self.object.IsReflection:
				wwobj = Deca.world.FindObject(self.object.ID)
				if len(wwobj):
					lres = wwobj[0][0].GetPropList()
					result.update([(_("Worldwide object's attributes"), lres.values()[1])])
				# if world-wide object found
			# if object is reflection
		# object's attributes taken
		graph = OrderedDict([
				(_("Graphical properties"),  OrderedDict([
					(_("Pen"), self._pen),
					(_("Brush"), self._brush),
					(_("TextColor"), self._textColourName),
					(_("Width"), self._width),
					(_("Height"), self._height),
				]))
			])
		if isinstance(result, OrderedDict):
			result.update(graph)
		else:
			result = graph
		return result
