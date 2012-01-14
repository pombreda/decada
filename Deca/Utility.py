# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Utility
# Purpose:     The DECA utility functions
#
# Author:      Stinger
#
# Created:     26.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import imp
import sys
from persistent.list import PersistentList
from persistent.cPersistence import Persistent
from persistent.mapping import PersistentMapping

__author__ = 'Stinger'

CodeObjectsModule = '_internal_co_mod'

def Filter(func, xs) :
	"""Filtering iterable object by applying the functor to each element

	:param func: functor to use in if statement for filter generator
	:param xs: iterable to be filtered
	:returns: :class:`dict` for dicts and :class:`PersistentMapping`, :class:`set` or :class:`frozenset` for
	 the corresponding arguments and :class:`list` for other argument's types"""
	if func is None:
		if isinstance(xs, dict) or isinstance(xs, PersistentMapping):
			f = lambda x, y: x and y
		else:
			f = lambda x: x
	else :
		f = func
	if isinstance(xs, list) or isinstance(xs, PersistentList):
		return [ x for x in xs if f(x) ]
	elif isinstance(xs, set):			return set (x for x in xs if f(x))
	elif isinstance(xs, frozenset):		return frozenset(x for x in xs if f(x))
	elif isinstance(xs, dict) or isinstance(xs, PersistentMapping):
		return {k:v for k, v in xs.items() if f(k, v)}
	else:								return [ x for x in xs if f(x) ]

def ImportPackage(pkg_name, pkg_path, type=imp.PKG_DIRECTORY):
	"""ImportPackage(pkg_name, pkg_path, type=imp.PKG_DIRECTORY)

	Implements importing for the packages and source files.

	:param pkg_name: name of the package in *sys.modules* dictionary
	:param pkg_path: path to package directory or file name to import
	:param type: type of source to import
	:type type: imp.PKG_DIRECTORY, imp.imp.PY_COMPILED, imp.imp.PY_SOURCE
	"""
	mod = None
	if type == imp.PY_SOURCE:
		fl = open(pkg_path)
		try:
			mod = imp.load_module(pkg_name, fl, pkg_path, ('', 'r', type))
		finally:
			fl.close()
	else:
		if not pkg_path in sys.path:
			sys.path.append(pkg_path)
		mod = imp.load_module(pkg_name, None, pkg_path, ('', 'r', type))
	if mod:
		sys.modules[pkg_name] = mod
		globals()[pkg_name] = mod
	# loaded!

def GetModule(pkg_name):
	"""Search given name in sys.modules dictionary

	:returns: :class:`module` object or *None*	"""
	return sys.modules.get(pkg_name)

def CompileCode(text, modname=CodeObjectsModule):
	"""Compiles given strin as Python code and place resulting code-object into the module with given name.

	:returns: :class:`module` object
	:raises: Any type of :class:`Exceptions` produced by compilation process"""
	co = compile(text, '', 'exec')
	mod = imp.new_module(modname)
	mod.__filename__ = 'Sampo_internal'
	sys.modules[modname] = mod
	exec(co, mod.__dict__, mod.__dict__)
	return mod
