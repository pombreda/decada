# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        PropertySheet
# Purpose:     Implement property sheet control
#
# Author:      Stinger
#
# Created:     20.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import wx.grid

from Editra.src import ed_style
import gettext
_ = gettext.gettext

__author__ = 'Stinger'
__revision__ = "$Revision: 0 $"

###########################################################################
## Class PropGridBlock
###########################################################################

class PropGridBlock ( wx.Panel ):

	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 227,225 ), style = wx.TAB_TRAVERSAL )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bTitleSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.stMark = wx.StaticText( self, wx.ID_ANY, ' ', wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stMark.Wrap( -1 )
		self.stMark.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		bTitleSizer.Add( self.stMark, 0, wx.ALL, 2 )


		bTitleSizer.AddSpacer( ( 5, 0), 0, wx.EXPAND, 2 )

		self.stTitle = wx.StaticText( self, wx.ID_ANY, _("MyLabel"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTitle.Wrap( -1 )
		self.stTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		bTitleSizer.Add( self.stTitle, 1, wx.ALL|wx.EXPAND, 2 )

		bSizer.Add( bTitleSizer, 0, wx.EXPAND, 0 )

		self.propGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.propGrid.CreateGrid( 0, 1 )
		self.propGrid.EnableEditing( True )
		self.propGrid.EnableGridLines( True )
		self.propGrid.EnableDragGridSize( False )
		self.propGrid.SetMargins( 0, 0 )

		# Columns
		self.propGrid.EnableDragColMove( False )
		self.propGrid.EnableDragColSize( True )
		self.propGrid.SetColLabelSize( 0 )
		self.propGrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

		# Rows
		self.propGrid.EnableDragRowSize( False )
		self.propGrid.SetRowLabelSize( 80 )
		self.propGrid.SetRowLabelAlignment( wx.ALIGN_LEFT, wx.ALIGN_CENTRE )

		# Label Appearance

		# Cell Defaults
		self.propGrid.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer.Add( self.propGrid, 1, wx.ALL|wx.EXPAND, 0 )

		self.SetSizer( bSizer )
		self.Layout()

		# Connect Events
		self.Bind( wx.EVT_SIZE, self.OnBlockSize )
		self.Bind(wx.EVT_PAINT, self.OnPaintMark)
		self.stMark.Bind( wx.EVT_LEFT_UP, self.OnTitleClick )
		self.stTitle.Bind( wx.EVT_LEFT_UP, self.OnTitleClick )
		self.propGrid.Bind( wx.grid.EVT_GRID_EDITOR_HIDDEN, self.OnFinishEdit )

		#wx.CallAfter(self.OnPaintMark)

	def __del__( self ):
		# Disconnect Events
		self.Unbind( wx.EVT_SIZE )
		#self.stMark.Unbind( wx.EVT_LEFT_UP, None )
		#self.stTitle.Unbind( wx.EVT_LEFT_UP, None )


	def UpdateColors(self, stm):
		cl = wx.Color()
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.stMark.SetForegroundColour(stm.GetDefaultForeColour())
		self.stTitle.SetForegroundColour(stm.GetDefaultForeColour())
		# grid elements
		sm = stm.GetItemByName('caret_line')
		cl.SetFromString(sm.back)
		self.propGrid.SetDefaultCellBackgroundColour( cl )
		self.propGrid.SetDefaultCellTextColour( stm.GetDefaultForeColour() )
		self.propGrid.SetLabelBackgroundColour( stm.GetDefaultBackColour() )
		self.propGrid.SetLabelTextColour( stm.GetDefaultForeColour() )
		self.Refresh()

	def AddProperty(self, label, value):
		if self.propGrid.AppendRows() :
			idx = self.propGrid.GetNumberRows() - 1
			self.propGrid.SetRowLabelValue(idx, label)
			self.propGrid.SetCellValue(idx, 0, str(value))
		# end of row addition
	
	# Virtual event handlers, overide them in your derived class
	def OnBlockSize( self, event ):
		w = self.GetClientSize().width - self.propGrid.GetRowLabelSize() - 20
		self.Layout()
		self.propGrid.SetColSize( 0, w)

	def OnTitleClick( self, event ):
		if self.propGrid.IsShown() :
			#self.stMark.Label = unichr(0x25b6)
			self.propGrid.Hide()
		else :
			#self.stMark.Label = unichr(0x25bc)
			self.propGrid.Show()
		self.GetParent().Layout()
		self.Refresh()

	def OnPaintMark(self, event = None):
		dc = wx.GCDC(wx.PaintDC(self))
		render = wx.RendererNative.Get()

		# Setup Brushes
		dc.SetBrush(wx.BLACK_BRUSH) #wx.Brush(self.stMark.GetForegroundColour()))
		markType = 0
		if self.propGrid.IsShown() :
			markType = wx.CONTROL_EXPANDED
		th = self.stMark.GetRect()
		hh = th.top + (th.GetHeight() - 8) / 2
		render.DrawTreeItemButton(self, dc, (th.left, hh, 16, 10), markType)

	def OnFinishEdit( self, event ):
		event.Skip()

###########################################################################
## Class PropGridPanel
###########################################################################

class PropGridPanel ( wx.Panel ):

	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 213,354 ), style = wx.TAB_TRAVERSAL )
		self.propObj = None
		self.styler = None
		self.blocks = []

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.bDictSizer = wx.BoxSizer( wx.VERTICAL )

		bSizer.Add( self.bDictSizer, 0, wx.EXPAND, 0 )

		bSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		divider = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer.Add( divider, 0, wx.ALL|wx.EXPAND, 2 )

		self.propTitle = wx.StaticText( self, wx.ID_ANY, _(""), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.propTitle.Wrap( -1 )
		self.propTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		bSizer.Add( self.propTitle, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.propDesc = wx.StaticText( self, wx.ID_ANY, _(""), wx.DefaultPosition, wx.Size( -1,42 ), wx.ST_NO_AUTORESIZE )
		self.propDesc.Wrap( -1 )
		bSizer.Add( self.propDesc, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.SetSizer( bSizer )
		self.Layout()

		# Connect Events
		self.Bind( wx.EVT_SIZE, self.OnSheetSize )

	def __del__( self ):
		# Disconnect Events
		self.Unbind( wx.EVT_SIZE )

	def SetPropObject(self, obj):
		""" Insert object into the Property Sheet to display it.
			Object must implements the GetPropList interface. This interface returns the dictionary with keys as
			the groups labels and values as dictionary with keys as property labels and values as property value objects
		"""
		if self.propObj is not None:
			# deregister notification
			if hasattr(self.propObj, "DropPropsNotify") :
				self.propObj.DropPropsNotify()
		if hasattr(obj, "GetPropList") :
			self.propObj = obj
			self.UpdateGrid()
		else :
			wx.MessageBox(_("Can't display properties for %s, because it hasn't GetPropList interface") % obj.__class__.__name__,
							_("Sampo Framework"), wx.OK | wx.CENTER | wx.ICON_ERROR)

	def UpdateColors(self, stm):
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		for block in self.blocks :
			if isinstance(block, PropGridBlock):
				block.UpdateColors(stm)

		self.propTitle.SetForegroundColour(stm.GetDefaultForeColour())
		self.propDesc.SetForegroundColour(stm.GetDefaultForeColour())
		self.Refresh()
		self.styler = stm

	def UpdateGrid(self):
		if self.propObj is not None :
			self.bDictSizer.Clear(True)
			self.blocks = []
			props = self.propObj.GetPropList(self)
			for nm in props :
				grp = PropGridBlock(self)
				grp.stTitle.Label = nm
				for pl in props[nm] :
					grp.AddProperty(pl, props[nm][pl])
				self.bDictSizer.Add(grp, 0, wx.ALL|wx.EXPAND, 0 )
				self.blocks.append(grp)
			# end of foreach groups
			self.Layout()
		#end of if
		if self.styler is not None :
			self.UpdateColors(self.styler)

	# Virtual event handlers, overide them in your derived class
	def OnSheetSize( self, event ):
		sz = self.GetClientSize()
		self.Layout()
		for block in self.blocks :
			if isinstance(block, PropGridBlock):
				block.SendSizeEvent()
