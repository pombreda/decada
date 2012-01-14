# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        NbookPanel
# Purpose:     Interface to implement main notebook panel
#
# Author:      Stinger
#
# Created:     14.11.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import gettext
from Editra.src import ed_glob
import PyShell

_ = gettext.gettext

__author__ = 'stinger'

###########################################################################
## Class NbookPanel
###########################################################################
class NbookPanel(wx.Panel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		wx.Panel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "Panel"
		self.Title = ""
		self.tabIndex = -1
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_FILE), wx.ART_MENU, wx.Size(16, 16))

	def UpdatePageTitle(self):
		"""Updates the notebook'spage title.
		Call 'SetTabIndex' first to store page index"""
		self.GetParent().SetPageText(self.tabIndex, self.Title)

	def GetSelection(self):
		"""Retursn selected page in the notebook"""
		parent = self.GetParent()
		return parent.GetSelection()

#	def SetSelection(self, idx):
#		parent = self.GetParent()
#		#parent.SetSelection(idx)

	def SetTabIndex(self, idx):
		"""Stores the page index in the notebook"""
		self.tabIndex = idx

	def GetTabIndex(self):
		"""Stores the page index in the notebook"""
		return self.tabIndex

	def DispatchToControl(self, evt):
		"""Dispatch events to the children"""
		evt.GetId()
		pass

	def GetTabImage(self):
		"""Get the Bitmap to use for the tab
		@return: wx.Bitmap (16x16)
		"""
		return self.icon

	def UpdateColors(self, stm):
		"""Apply style from given Style Manager to the page"""
		pass

	def UpdateView(self, event):
		"""Renew view representation"""
		if event:
			event.GetId()
		pass

	def GetParams(self):
		return None

###########################################################################
## Class PyShellView
###########################################################################
class PyShellView(NbookPanel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "Console"
		self.Title = _("Console")
		self.tabIndex = -1
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PYSHELL), wx.ART_MENU, wx.Size(16, 16))

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.shell = PyShell.EdPyShell(self)

		bSizer.Add( self.shell, proportion=1, flag=wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

	def UpdateColors(self, stm):
		self.shell.SetShellTheme(stm.GetCurrentStyleSetName())