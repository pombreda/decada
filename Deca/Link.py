# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Link
# Purpose:     A link between two objects
#
# Author:      Stinger
#
# Created:     19.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
from persistent import Persistent

__author__ = 'Stinger'

class DecaLink(Persistent):
	"""A link between two objects.

	Link has three mandatory properties:

	* **StartObject** - the object's identifier (:class:`UUID`) for the starting point
	* **FinishObject** - the object's identifier (:class:`UUID`) for the finishing point
	* **Directional** - does this Link has diretion

	Also, link can have any set of the properties. Be aware that the Link controls mutation only the properties list itself.
	If you put mutable object into the Link's property and then change such object, the Link information can be unchanged. Use the
	:attr:`Modified` property to notify the Link about changes.

	:param obj_start: object's identifier (:class:`UUID`) for the starting point
	:param obj_fin: object's identifier (:class:`UUID`) for the finishing point
	:param direct: is this link directional or none"""
	def __init__(self, obj_start = None, obj_fin = None, direct=False):
		self.StartObject = obj_start
		self.FinishObject = obj_fin
		self.Directional = direct

	@property
	def ID(self):
		"""Link's identifier."""
		return hash("%s%s" % (self.StartObject, self.FinishObject))

	@property
	def Modified(self):
		""" Is this link modifyed sinece extracted from DB """
		return self._p_changed

	@Modified.setter
	def Modified(self, value):	self._p_changed = value

	def copy(self):
		"""Creates shallow copy of the link.

		**Note:** both new and original links will have same identifiers!
		"""
		obj = DecaLink()
		for k in self.__dict__.keys():
			obj.__setattr__(k, self.__getattribute__(k))
		return obj

	@staticmethod
	def BuildID(obj_start = None, obj_fin = None):
		"""Satatic method to calculate link ID withou link creation.

		:param obj_start: object's identifier (:class:`UUID`) for the starting point
		:param obj_fin: object's identifier (:class:`UUID`) for the finishing point
		"""
		return hash("%s%s" % (obj_start, obj_fin))
