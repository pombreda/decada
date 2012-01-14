# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        World
# Purpose:     The DECA world object
#
# Author:      Stinger
#
# Created:     19.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import platform
from persistent.mapping import PersistentMapping
import wx
import tempfile
import zipfile
import shutil
from collections import OrderedDict
from Deca.Layer import DecaRepo, DecaLayer, DecaLayerStorage, DecaRepoStorage
import Editra.src.ed_glob as ed_glob
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import gettext
_ = gettext.gettext

__author__ = 'Stinger'
ID_Repository = '@repository'

def walk_visit(arg, dirname, flist):
	'''Helper function to correctly save the world'''
	zipper = arg[0]
	base = arg[1]
	base = dirname.replace(base, '')
	for f in flist :
		try:
			zipper.write(os.path.join(dirname, f), os.path.join(base, f))
		except Exception as cond :
			wx.GetApp().log("[Deca.World][warn] %s" % cond)

class DecaWorld:
	"""The DECA world object.

	This object controls the database and the file structure for the DECA world.
	The constructor argument *filename* allows restore previously saved world from file."""

	ID_Repository = '@repository'
	"""Internal layer to store repository: templates, objects and shapes. It always exists,
	and can't be removed."""

	ID_Configuration = '@configuration'
	"""Internal pseudo-layer to store configuration data.
	
	This storage is just the dictionary to save arbitrary data in the world's storage.
	It always exists, and can't be removed."""

	def __init__(self, filename = None):
		self.roots = None
		self.propsGrid = None
		self.Modified = False
		self.Initial = False
		self.db_path = None
		self.layers = {}
		self.Filename = filename
		self.wfs = tempfile.mkdtemp(suffix='.deca')
		if filename is not None:
			# open filesystem
			try:
				f = zipfile.ZipFile(self.Filename)
				f.extractall(self.wfs)
				f.close()
				self.db_path = os.path.join(self.wfs, 'database')
				self.db_path = os.path.join(self.db_path, 'filestorage.sampo')
				if not os.path.exists(self.db_path) :
					self.db_path = None
			except Exception:
				self.db_path = None
		if self.db_path is None :
			# create new world filesystem if file not given, or error occurred
			if filename is None :
				self.Initial = True
			try:
				# create initial structure
				os.makedirs(os.path.join(self.wfs, 'profiles'))
				os.makedirs(self.PixmapsPath)
				os.makedirs(os.path.join(self.wfs, 'database'))
				os.makedirs(self.EnginesPath)
				os.makedirs(os.path.join(self.EnginesPath, 'Default'))	# engines for 'Default' template
				os.makedirs(os.path.join(self.EnginesPath, 'layer'))	# engines for layer
				os.makedirs(self.ReportsPath)
				os.makedirs(self.ResultsPath)
				os.makedirs(self.AttachmentsPath)

				self.db_path = os.path.join(self.wfs, 'database')
				self.db_path = os.path.join(self.db_path, 'filestorage.sampo')

				cname = os.path.join(ed_glob.CONFIG['GLOBAL_PROFILE_DIR'], 'default.ppb')
				f = open(cname, 'rb')
				store = open(os.path.join(self.wfs, 'profiles' + os.sep + 'default.ppb'), 'wb')
				store.write(f.read())
				store.close()
			except Exception as cond:
				wx.MessageBox(_("Can't create world's storage!\n%s\nExiting...") % cond, _("Sampo Framework"), wx.OK | wx.CENTER | wx.ICON_ERROR)
				wx.GetApp().Exit()
		# initialize database
		ed_glob.CONFIG['PROFILE_DIR'] = os.path.join(self.wfs, 'profiles')

		# drop database indexes if platrorm doesn't match with previous save
		try :
			saved_platform = ''
			try:
				f = open(os.path.join(self.wfs, 'profiles' + os.sep + 'platform.dat'), 'r')
				saved_platform = f.read()
				f.close()
			except Exception:
				pass
			if saved_platform != platform.system() :
				os.unlink(self.db_path + '.index')
				os.unlink(self.db_path + '.tmp')
		except Exception:
			pass

		try:
			self.storage = FileStorage(self.db_path)
		except Exception:
			# try to remove indexes and reload base
			try:
				os.unlink(self.db_path + '.index')
				os.unlink(self.db_path + '.tmp')
				os.unlink(self.db_path + '.lock')
			except Exception:
				pass
			self.storage = FileStorage(self.db_path)
		self.odb = DB(self.storage)
		self.connection = self.odb.open()
		self.roots = self.connection.root()
		self.transaction = self.connection.transaction_manager.begin()
		# always create repository
		if self.Initial :
			self.roots[self.ID_Repository] = DecaRepoStorage()
			self.roots[self.ID_Configuration] = PersistentMapping()
		self.layers[self.ID_Repository] = DecaRepo(self, self.ID_Repository)
		# world created

	def __del__(self):
		self.Destroy()

	def _commit(self):
		self.transaction.commit()
		self.transaction = self.connection.transaction_manager.begin()

	def Destroy(self):
		"""Destroy(self)

		Finalize world usage. Save world and delete the directory tree"""
		if not self.Initial :
			self.Save()
		self.odb.close()
		shutil.rmtree(self.wfs, True)

	def Save(self, fname = None):
		"""Save(self, String fname = None)

		Flush current world's storage. Stores into the reviously given file, or to the
		file given as function parameter. If no file name given and world dosen't created
		from file or never was saved the diagnostical message appear.
		
		:param fname: file name to store the world to. May be *None* to use previously given file name
		:type fname: string or None"""
		if self.Initial and fname is None:
			wx.MessageBox(_("Can't save world's storage without path-name"), _("Sampo Framework"), wx.OK | wx.CENTER | wx.ICON_ERROR)
			return

		if self.Initial and fname is not None:
			# move to normal file
			self.Filename = fname
			self.Initial = False
		# Save
		try:
			self._commit()
			self.odb.pack()
			f = zipfile.ZipFile(self.Filename, 'w')
			arg = (f, self.wfs)
			os.path.walk(self.wfs, walk_visit, arg)
			f.close()
			self.Modified = False
			# save platform marker
			f = open(os.path.join(self.wfs, 'profiles' + os.sep + 'platform.dat'), 'w')
			f.write(platform.system())
			f.close()
		except Exception as cond:
			wx.MessageBox(_("Can't save world's storage!\n%s") % cond, _("Sampo Framework"), wx.OK | wx.CENTER | wx.ICON_ERROR)
		# end of Save

	def GetLayer(self, name):
		"""GetLayer(self, String name)

		Return Deca.Layer with th given name from the world. If layer with given name doesn't exists
		the new layer created.
		
		:param name: name of the desired layer
		:type name: string or None
		:returns: :class:`Deca.Layer` object"""
		if name in self.layers.keys():
			return self.layers[name]

		if name not in self.roots.keys() :
			self.roots[name] = DecaLayerStorage()
		self.layers[name] = DecaLayer(self, name)
		return self.layers[name]

	def GetLayerList(self):
		"""Build list of layers names for layers existing in this world.

		:returns: the list of layers names existing in this world"""
		return self.roots.keys()
		
	def DeleteLayer(self, name):
		"""DeleteLayer(self, name)

		Removes given layer from world. This operation **destroes all data on this layer** and can't be undone.
		
		:param name: name of the desired layer
		:type name: string or None"""
		if name in self.layers.keys():
			del self.layers[name]
		if name in self.roots.keys():
			del self.roots[name]

	def GetPropList(self, holder = None) :
		self.propsGrid = holder
		result = OrderedDict([
			("World's properties",  OrderedDict([
				("Layers", len(self.roots.keys()) - 2)
			]))
		])
		return result

	def FindObject(self, oid, includeReflections=False):
		"""Search for object(s) with given ID through all layers in the world.
		
		:param oid: Object identifier
		:param includeReflections: need to include reflections into results? False by default.
		:returns: list of two-values tuples. First value - the object reference, second - the layer name"""
		result = []
		for ln,l in self.roots.items():
			if ln != self.ID_Configuration:
				for oi,oo in l.objects.items():
					if oi == oid and (not oo.IsReflection or includeReflections):
						result.append((oo, ln))
					# check for reflections
				# foreach object
			# not configuration layer
		# foreach layer
		return result

	def GetShapes(self):
		"""Search for object(s) with given ID through all layers in the world.

		:returns: list of string for names existing shapes"""
		try:
			return [os.path.splitext(f)[0] for f in os.listdir(self.ShapesPath) if os.path.splitext(f)[1].lower() == '.py']
		except Exception:
			return []

	@property
	def Configuration(self):
		"""Dictionary of configuration values"""
		return self.roots[self.ID_Configuration]

	@property
	def EnginesPath(self):
		"""String for current used OS path there engines hierarchy stored"""
		return os.path.join(self.wfs, 'engines')

	@property
	def ReportsPath(self):
		"""String for current used OS path there reports hierarchy stored"""
		return os.path.join(self.wfs, 'reports')

	@property
	def ResultsPath(self):
		"""String for current used OS path there reports results are stored"""
		return os.path.join(self.wfs, 'results')

	@property
	def AttachmentsPath(self):
		"""String for current used OS path there reports attachments are stored"""
		return os.path.join(self.wfs, 'attachments')

	@property
	def PixmapsPath(self):
		"""String for current used OS path there world-related images are stored"""
		return os.path.join(self.wfs, 'pixmaps')

	@property
	def ShapesPath(self):
		"""String for current used OS path there shapes definitions are stored"""
		return os.path.join(self.wfs, 'shapes')
