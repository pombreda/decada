# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ScEditor
# Purpose:     Implements panel (child window) with the source script's editor
#
# Author:      Stinger
#
# Created:     16.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import wx
import Deca
from Editra.src import ed_editv, ed_glob, ed_search
import gettext
from Editra.src.cbrowser import CodeBrowserTree
from SearchBar import SearchBar
from NbookPanel import NbookPanel
from Reporter import ReportGenerator

_ = gettext.gettext

###########################################################################
## Class EdtHolder
###########################################################################
class EdtHolder(wx.Panel):
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		wx.Panel.__init__ ( self, parent, id, pos, size, style, name )

	def UpdatePageTitle(self):
		"""Updates the notebook'spage title.
		Call 'SetTabIndex' first to store page index"""
		self.GetParent().GetParent().UpdatePageTitle()

	def GetSelection(self):
		"""Retursn selected page in the notebook"""
		return self.GetParent().GetParent().GetSelection()

	def SetSelection(self, *idx):
		return idx

###########################################################################
## Class EditorPanel
###########################################################################
class EditorPanel(NbookPanel):
	"""Tab editor view for main notebook control.
	Contains local toolbar and the editor itself """

	ED_TypeScript = wx.stc.STC_LEX_PYTHON
	ED_TypeReport = wx.stc.STC_LEX_XML

	def __init__(self, edType, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		"""Initialize the editor view"""
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "Text"
		self.LastCbWidth = -200

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.mtb = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.mtb.AddTool(wx.ID_FORWARD, wx.ArtProvider_GetBitmap(str(ed_glob.ID_NEXT_MARK), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Run"), longHelpString= _("Execute engine as module"))
		self.mtb.AddTool(wx.ID_SAVE, wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAVE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Save"), longHelpString= _("Save engine text"))
		self.mtb.AddTool(wx.ID_SAVEAS, wx.ArtProvider_GetBitmap(str(ed_glob.ID_NEW), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Save as..."), longHelpString= _("Save engine text as new engine"))
		self.mtb.AddSeparator()
		self.mtb.AddTool(wx.ID_UNDO, wx.ArtProvider_GetBitmap(str(ed_glob.ID_UNDO), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Undo"), longHelpString= _("Undo previous operation"))
		self.mtb.AddTool(wx.ID_REDO, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REDO), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Redo"), longHelpString= _("Redo reverted operation"))
		self.mtb.AddTool(wx.ID_PREVIEW, wx.ArtProvider_GetBitmap(str(ed_glob.ID_METHOD_TYPE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("CodeBrowser"), longHelpString= _("Toggle CodeBrowser window"))
		#self.mtb.AddLabelTool( wx.ID_ANY, _("tool"), wx.NullBitmap, wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString )
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=5 )

		self.split = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )

		self.panLeft = EdtHolder( self.split, wx.ID_ANY )
		bSzLeft = wx.BoxSizer( wx.VERTICAL )

		self.tx = ed_editv.EdEditorView(self.panLeft)
		if edType == self.ED_TypeScript:
			self.tx.ConfigureLexer('py')
		elif edType == self.ED_TypeReport:
			self.tx.ConfigureLexer('xml')
		self.tx.ConfigureAutoComp()
		bSzLeft.Add( self.tx, proportion=1, flag=wx.EXPAND |wx.ALL, border=0 )

		self.commandBar = wx.Panel(self.panLeft) #SearchBar( self.panLeft )
		self.commandBar.Hide()
		bSzLeft.Add( self.commandBar, proportion=0, flag=wx.EXPAND |wx.ALL, border=0 )

		self.panLeft.SetSizer( bSzLeft )
		self.panLeft.Layout()
		bSzLeft.Fit( self.panLeft )

		self.panRight = wx.Panel( self.split, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSzRight = wx.BoxSizer( wx.VERTICAL )

		self.cbrowser = CodeBrowserTree(self.panRight)
		self.cbrowser.SetCtrl(self.tx)
		bSzRight.Add( self.cbrowser, proportion=1, flag=wx.EXPAND |wx.ALL, border=0 )

		self.panRight.SetSizer( bSzRight )
		self.panRight.Hide()
		self.panRight.Layout()
		bSzRight.Fit( self.panRight )

		self.split.Initialize(self.panLeft) #SplitVertically( window1=self.panLeft, window2=self.panRight, sashPosition=400 )
		self.split.SetSashGravity(1)
		bSizer.Add( self.split, proportion=1, flag=wx.EXPAND |wx.ALL, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self._searchctrl = ed_search.SearchController(self, self.GetStc)

		self.Bind(wx.EVT_MENU, self.DispatchToControl)
		self.Bind(wx.stc.EVT_STC_CHANGE, self.OnChanged)

	def GetParams(self):
		fn = self.GetFileName()
		if self.tx.Lexer == self.ED_TypeScript:
			fn = fn.replace(Deca.world.EnginesPath, '')
		elif self.tx.Lexer == self.ED_TypeReport:
			fn = fn.replace(Deca.world.ReportsPath, '')
		if fn.startswith(os.path.sep):
			fn = fn[1:]
		return fn, self.tx.Lexer

	def GetStc(self):
		return self.tx

	def SetSelection(self, idx):
		return idx
	
	def UpdatePageTitle(self):
		ttl = self.tx.GetTitleString()
		parent = self.GetParent()
		parent.SetPageText(self.GetTabIndex(), ttl)

	def OnChanged(self, evt):
		evt.GetId()
		self.UpdatePageTitle()
		Deca.world.Modified = True

	def UpdateColors(self, stm):
		self.tx.UpdateAllStyles(stm.GetCurrentStyleSetName())

	def DispatchToControl(self, evt):
		evt_id = evt.GetId()
		if evt_id == wx.ID_SAVE:
			self.tx.SaveFile(self.tx.GetFileName())
			self.UpdatePageTitle()
		elif evt_id == wx.ID_FIND:
			if not isinstance(self.commandBar, SearchBar):
				cb = SearchBar( self.panLeft )
				self.panLeft.GetSizer().Replace(self.commandBar, cb)
				self.commandBar.Destroy()
				self.commandBar = cb
			self.commandBar.Show()
			self.commandBar.ctrl.SetFocus()
			self.panLeft.Layout()
			self.Layout()
		elif evt_id == wx.ID_PREVIEW:
			if self.split.IsSplit(): 
				self.LastCbWidth = self.split.GetSashPosition()
				self.split.Unsplit()
			else:
				self.split.SplitVertically( window1=self.panLeft, window2=self.panRight, sashPosition=self.LastCbWidth )
				self.cbrowser.OnUpdateTree(force=True)
			self.Layout()
			self.GetParent().Update()
		elif evt_id == wx.ID_SAVEAS:
			pass
		elif evt_id == wx.ID_FORWARD:
			self.RunCode()
		else:
			self.tx.ControlDispatch(evt)

	def GetTabImage(self):
		"""Get the Bitmap to use for the tab
		@return: wx.Bitmap (16x16)
		"""
		return self.tx.GetTabImage()

	def GetFileName(self):
		return self.tx.GetFileName()

	def RunCode(self):
		self.tx.SaveFile(self.tx.GetFileName())
		self.UpdatePageTitle()
		fname = self.tx.GetFileName()
		if self.tx.Lexer == self.ED_TypeScript:
			fname = fname.replace(Deca.world.EnginesPath, '')
			fl = None
			try:
				fl = open(self.tx.GetFileName(), 'r')
				exec fl in globals()
			except Exception as cond:
				wx.MessageBox(_("Error execution %s!\n%s") % (fname, cond), _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
				wx.GetApp().log("[exec][err] %s" % cond)
			finally:
				if fl : fl.close()
		elif self.tx.Lexer == self.ED_TypeReport:
			gen = ReportGenerator(fileName=fname)
			gen.Generate(self)
		else:
			wx.MessageBox(_("Sorry! i don't know how to run such file."), _("Sampo Framewok"), wx.OK|wx.ICON_WARNING)
		pass
