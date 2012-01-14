# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Deca
# Purpose:     Main module of the Deca structure
#
# Author:      Stinger
#
# Created:     18.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
__author__ = 'Stinger'
__revision__ = "$Revision: 0 $"

from . import Object
from . import Attribute
from . import Link
from . import World
from . import Layer

__all__ = ["Object", "Link", "Attribute", "World", "Layer"]

Object = Object.__dict__['DecaObject']
Link = Link.__dict__['DecaLink']
Attribute = Attribute.__dict__['DecaAttr']
World = World.__dict__['DecaWorld']
Layer = Layer.__dict__['DecaLayer']

world = None

def CreateWorld(fname = None) :
	global world
	if world:
		world.Destroy()
	world = World(fname)
	return world
