# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        CustomGrid
# Purpose:     Implements grid to work with non-string data
#
# Author:      Stinger
#
# Created:     24.11.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
import string
import wx
import wx.grid as gridlib
import gettext
from Editra.src import ed_glob

_ = gettext.gettext

__author__ = 'aabramov'

###########################################################################
## Class EditIterable
###########################################################################
class EditIterable ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Edit"), pos = wx.DefaultPosition, size = (400,350), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )
		self.value = None

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bSizerTb = wx.BoxSizer( wx.HORIZONTAL )

		self.btnAddRow = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizerTb.Add( self.btnAddRow, 0, wx.ALL, 2 )

		self.btnDelRow = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REMOVE), wx.ART_MENU, wx.Size(16, 16)),
										  wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizerTb.Add( self.btnDelRow, 0, wx.ALL, 2 )

		stType = wx.StaticText( self, wx.ID_ANY, _("Type of new element:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		stType.Wrap( -1 )
		bSizerTb.Add( stType, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2 )

		chTypeChoices = [ _("string"), _("int"), _("float"), _("boolean"), _("<list>"), _("<set>"), _("<tuple>"), _("<dict>") ]
		self.chType = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, chTypeChoices, 0 )
		self.chType.SetSelection( 0 )
		bSizerTb.Add( self.chType, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2 )

		bSizer.Add( bSizerTb, 0, wx.EXPAND, 2 )

		self.gridData = CustomGrid( self, wx.ID_ANY, style=0 )

		# Grid
		self.gridData.CreateGrid( 0, 0 )
		self.gridData.EnableEditing( True )
		self.gridData.EnableGridLines( True )
		self.gridData.EnableDragGridSize( False )
		self.gridData.SetMargins( 0, 0 )

		# Columns
		self.gridData.EnableDragColMove( False )
		self.gridData.EnableDragColSize( True )
		self.gridData.SetColLabelSize( 30 )
		self.gridData.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

		# Rows
		self.gridData.EnableDragRowSize( True )
		self.gridData.SetRowLabelSize( 80 )
		self.gridData.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

		# Label Appearance

		# Cell Defaults
		self.gridData.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer.Add( self.gridData, 1, wx.ALL|wx.EXPAND, 2 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize();
		bSizer.Add( sdbSizer, 0, wx.ALL|wx.EXPAND, 5 )

		self.SetSizer( bSizer )
		self.Layout()
		#bSizer.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnAddRow.Bind( wx.EVT_BUTTON, self.OnAddRow )
		self.btnDelRow.Bind( wx.EVT_BUTTON, self.OnDelRow )
		self.sdbSizerOK.Bind( wx.EVT_BUTTON, self.OnOk )

	def __del__( self ):
		# Disconnect Events
		pass

	def SetDataName(self, name):
		self.SetTitle(self, _("Edit - %s") % name)

	def SetData(self, val):
		self.value = val
		self.gridData.ClearGrid()
		if type(self.value) == list or isinstance(self.value, PersistentList) or \
					type(self.value) == set or type(self.value) == tuple :
			self.gridData.AppendCols(1)
			self.gridData.SetColSize( 0, width=200 )
			self.gridData.SetColLabelValue(0, _("Item"))
			self.gridData.AppendRows(len(self.value))
			row = 0
			for i in self.value:
				self.gridData.SetCellValue(row, 0, i)
				self.gridData.SetCellRenderer(row, 0, ToStringRenderer())
				self.gridData.SetCellEditor(row, 0, ToStringEditor())
				row += 1

		elif type(self.value) == dict or isinstance(self.value, PersistentMapping) :
			self.gridData.AppendCols(2)
			self.gridData.SetColSize( 0, width=100 )
			self.gridData.SetColSize( 0, width=150 )
			self.gridData.SetColLabelValue(0, _("Key"))
			self.gridData.SetColLabelValue(1, _("Value"))
			self.gridData.AppendRows(len(self.value))
			row = 0
			for k,v in self.value.items():
				self.gridData.SetCellValue(row, 0, k)
				self.gridData.SetCellValue(row, 1, v)
				self.gridData.SetCellRenderer(row, 0, ToStringRenderer())
				self.gridData.SetCellEditor(row, 0, ToStringEditor())
				self.gridData.SetCellRenderer(row, 1, ToStringRenderer())
				self.gridData.SetCellEditor(row, 1, ToStringEditor())
				row += 1
		else:
			self.gridData.AppendCols(1)
			self.gridData.SetColSize( 0, width=250 )
			self.gridData.SetColLabelValue(0, _("Item"))
			self.gridData.AppendRows(1)
			self.gridData.SetCellValue(0, 0, self.value)
			self.gridData.SetCellRenderer(0, 0, ToStringRenderer())
			self.gridData.SetCellEditor(0, 0, ToStringEditor())
			# disable buttons
			self.btnAddRow.Disable()
			self.btnDelRow.Disable()
		pass

	def GetData(self):
		# rebuild data from grid
		if type(self.value) == list or isinstance(self.value, PersistentList) :
			vl = self.value.__class__()
			for x in xrange(self.gridData.GetNumberRows()) :
				vl.append(self.gridData.GetCellRawValue(row=x, col=0))
			self.value = vl
		elif type(self.value) == set :
			vl = self.value.__class__()
			for x in xrange(self.gridData.GetNumberRows()) :
				vl.add(self.gridData.GetCellRawValue(row=x, col=0))
			self.value = vl
		elif type(self.value) == tuple :
			vl = []
			for x in xrange(self.gridData.GetNumberRows()) :
				vl.append(self.gridData.GetCellRawValue(row=x, col=0))
			self.value = tuple(vl)
		elif type(self.value) == dict or isinstance(self.value, PersistentMapping) :
			vl = self.value.__class__()
			for x in xrange(self.gridData.GetNumberRows()) :
				k = self.gridData.GetCellRawValue(row=x, col=0)
				v = self.gridData.GetCellRawValue(row=x, col=1)
				vl[k] = v
			self.value = vl
		else:
			self.value = self.gridData.GetCellRawValue(0, 0)
		return self.value

	# Virtual event handlers, overide them in your derived class
	def OnAddRow( self, event ):
		self.gridData.AppendRows()
		pos = self.gridData.GetNumberRows() - 1
		if pos >= 0:
			cell = 0
			if type(self.value) == dict or isinstance(self.value, PersistentMapping) :
				cell = 1
			val = None
			# chTypeChoices = [ _("string"), _("int"), _("float"), _("<list>"), _("<set>"), _("<tuple>"), _("<dict>") ]
			if self.chType.GetSelection() == 0:
				val = ''
			elif self.chType.GetSelection() == 1:
				val = 0
			elif self.chType.GetSelection() == 2:
				val = 0.1
			elif self.chType.GetSelection() == 3:
				val = 0.1
			elif self.chType.GetSelection() == 4:
				val = False
			elif self.chType.GetSelection() == 5:
				val = set()
			elif self.chType.GetSelection() == 6:
				val = tuple()
			elif self.chType.GetSelection() == 7:
				val = {}
			self.gridData.SetCellValue(pos, cell, val)
			self.gridData.SetCellRenderer(pos, cell, ToStringRenderer())
			self.gridData.SetCellEditor(pos, cell, ToStringEditor())
		event.Skip()

	def OnDelRow( self, event ):
		pos = self.gridData.GetSelectedRows()
		if len(pos) >= 0 :
			for x in pos:
				self.gridData.DeleteRows(x)
			# end for selected
		# end deletion
		event.Skip()

	def OnOk( self, event ):
		self.gridData.DisableCellEditControl()
		event.Skip()

	def OnCancel( self, event ):
		self.gridData.DisableCellEditControl()
		event.Skip()

###########################################################################
## Class CellEditor
###########################################################################
class CellEditor ( wx.Control ):
	def __init__( self, parent, id ):
		wx.Control.__init__ ( self, parent, id = id )
		self.log = wx.GetApp().GetLog()
		self.value = None
		self._easyMode = False

		bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.txtView = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		bSizer.Add( self.txtView, proportion=1, flag=wx.EXPAND|wx.LEFT, border=2 )

		self.btn = wx.Button( self, wx.ID_ANY, _("..."), wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		bSizer.Add( self.btn, proportion=0, flag=wx.ALL|wx.EXPAND, border=0 )

		self.inChild = False
		self.holder = None

		self.SetSizer( bSizer )
		self.Layout()
		self.Bind(wx.EVT_BUTTON, self.OnButton, self.btn)
		self.txtView.Bind(wx.EVT_KILL_FOCUS, self.OnFocus)

	def __del__( self ):
		self.log("[CellEditor][dbg] del")
		pass

	def OnButton(self, event):
		dlg = EditIterable(self.GetParent())
		dlg.SetData(self.value)
		self.inChild = True
		if dlg.ShowModal() == wx.ID_OK:
			self.SetValue(dlg.GetData())
		self.inChild = False
		event.Skip()

	def SetSize( self, rect ):
		wx.Control.SetDimensions ( self, rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE)
		self.Layout()
		#self.btn.SetDimensions(rect.width - rect.height, 0, rect.height, rect.height,wx.SIZE_ALLOW_MINUS_ONE)
		#self.btn.Update()

	# Other methods
	def SetValue(self, val):
		self.value = val
		self._easyMode = False
		self.btn.Show()
		if type(self.value) == list or isinstance(self.value, PersistentList) :
			text = _("<list>: %i elem(s)") % len(self.value)
			self.txtView.Disable()
		elif type(self.value) == dict or isinstance(self.value, PersistentMapping) :
			text = _("<dict>: %i elem(s)") % len(self.value.keys())
			self.txtView.Disable()
		elif type(self.value) == set :
			text = _("<set>: %i elem(s)") % len(self.value)
			self.txtView.Disable()
		elif type(self.value) == tuple :
			text = _("<tuple>: %i elem(s)") % len(self.value)
			self.txtView.Disable()
		else:
			text = str(self.value)
			self.txtView.Enable()
			self.btn.Hide()
			self._easyMode = True
		self.txtView.Value = text
		self.Layout()

	def GetValue(self):
		if self._easyMode:
			try:
				self.value = self.value.__class__(self.txtView.Value)
			except Exception as conv:
				self.log("[CellEditor][warn] Can't create %s from string: %s" % (self.value.__class__, conv))
				self.value = self.txtView.Value
		return self.value

	def Commit(self):
		self.txtView.SetInsertionPointEnd()
		self.txtView.SetFocus()

	def OnFocus(self, evt):
		self.log("[CellEditor][dbg] OnFocus state = %s" % self.inChild)
		if not self.inChild and self.holder is not None:
			self.log("[CellEditor][dbg] OnFocus says to destroy")
			grid = self.Parent.Parent # must be a grid
			if isinstance(grid, gridlib.Grid):
				grid.DisableCellEditControl()

###########################################################################
## Class ToStringEditor
###########################################################################
class ToStringEditor(gridlib.PyGridCellEditor):
	def __init__(self):
		self.log = wx.GetApp().GetLog()
		#self.log.write("[ToStringEditor][dbg] ctor")
		self._control = None
		gridlib.PyGridCellEditor.__init__(self)

	def __del__(self):
		#self.log.write("[ToStringEditor][dbg] del")
		if self._control :
			self.SetControl(None)

	def Create(self, parent, id, evtHandler):
		self.log.write("[ToStringEditor][dbg] Create  from %s" % parent)
		#self._control = wx.TextCtrl( parent, id, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.NO_BORDER )
		self._control = CellEditor(parent, id)
		self._control.holder = self
		#self._control.SetInsertionPoint(0)
		self.SetControl(self._control)
		#if evtHandler:
		#	self._control.btn.PushEventHandler(evtHandler)

	def SetSize(self, rect):
		self.log.write("[ToStringEditor][dbg] SetSize %s" % rect)
		self._control.SetSize(rect)
		#self._control.SetDimensions ( rect.x, rect.y, rect.width+2, rect.height+2, wx.SIZE_ALLOW_MINUS_ONE)

	def Show(self, show, attr):
		self.log.write("[ToStringEditor][dbg] Show(self, %s, %s)" % (show, attr))
		#super(ToStringEditor, self).Show(show, attr)
		self._control.Show(show)

	def PaintBackground(self, rect, attr):
		self.log.write("[ToStringEditor][dbg] PaintBackground")

	def BeginEdit(self, row, col, grid):
		self.log.write("[ToStringEditor][dbg] BeginEdit (%d,%d)" % (row, col))
		self.startValue = grid.GetCellRawValue(row, col)
		self._control.SetValue(self.startValue)
		self._control.Commit()
		#self._control.SetInsertionPointEnd()
		#self._control.SetFocus()

	def EndEdit(self, row, col, grid):
		self.log.write("[ToStringEditor][dbg] EndEdit (%d,%d)" % (row, col))
		changed = False

		val = self._control.GetValue()

		if val != self.startValue:
			changed = True
			grid.SetCellValue(row, col, val) # update the table

		self.startValue = ''
		self._control.SetValue('')
		self.Detach()
		return changed

	def Reset(self):
		self.log.write("[ToStringEditor][dbg] Reset")
		self._control.SetValue(self.startValue)
		self._control.Commit()

	def IsAcceptedKey(self, evt):
		"""
		Return True to allow the given key to start editing: the base class
		version only checks that the event has no modifiers.  F2 is special
		and will always start the editor.
		"""
		self.log.write("[ToStringEditor][dbg] IsAcceptedKey: %d\n" % (evt.GetKeyCode()))

		## We can ask the base class to do it
		#return super(MyCellEditor, self).IsAcceptedKey(evt)

		# or do it ourselves
		return (not (evt.ControlDown() or evt.AltDown()) and
					evt.GetKeyCode() != wx.WXK_SHIFT)

	def StartingKey(self, evt):
		"""
		If the editor is enabled by pressing keys on the grid, this will be
		called to let the editor do something about that first key if desired.
		"""
		self.log.write("[ToStringEditor][dbg] StartingKey %d\n" % evt.GetKeyCode())
		key = evt.GetKeyCode()
		ch = None
		if key in [ wx.WXK_NUMPAD0, wx.WXK_NUMPAD1, wx.WXK_NUMPAD2, wx.WXK_NUMPAD3, 
					wx.WXK_NUMPAD4, wx.WXK_NUMPAD5, wx.WXK_NUMPAD6, wx.WXK_NUMPAD7, 
					wx.WXK_NUMPAD8, wx.WXK_NUMPAD9
					]:

			ch = chr(ord('0') + key - wx.WXK_NUMPAD0)

		elif key < 256 and key >= 0 and chr(key) in string.printable:
			ch = chr(key)
		elif key == wx.WXK_RETURN:
			evt.SetKeyCode(wx.WXK_F2)

		if ch is not None:
			# For this example, replace the text.  Normally we would append it.
			#self._tc.AppendText(ch)
			if self._control.txtView.Enabled:
				self._control.SetValue(ch)
				self._control.txtView.SetInsertionPointEnd()
		else:
			evt.Skip()

	def StartingClick(self):
		self.log.write("[ToStringEditor][dbg] StartingClick")

	def Destroy(self):
		"""final cleanup"""
		self.log.write("[ToStringEditor][dbg] Destroy")
		self.SetControl(None)
		if self._control :
			#self._control.
			self._control = None
		super(ToStringEditor, self).Destroy()

	def Detach(self):
		self.SetControl(None)
		if self._control :
			#self._control.Destroy()
			self._control = None

	def Clone(self):
		return ToStringEditor()

###########################################################################
## Class ToStringRenderer
###########################################################################
class ToStringRenderer(gridlib.PyGridCellRenderer):
	def __init__(self):
		gridlib.PyGridCellRenderer.__init__(self)

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		dc.SetBackgroundMode(wx.SOLID)
		dc.SetBrush(wx.Brush(attr.GetBackgroundColour(), wx.SOLID))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangleRect(rect)
		dc.SetBackgroundMode(wx.TRANSPARENT)
		dc.SetFont(attr.GetFont())
		dc.SetTextForeground(attr.GetTextColour())
		val = grid.GetCellRawValue(row, col)
		text = str(val)
		if type(val) == list or isinstance(val, PersistentList) :
			text = _("list(%i)%s") % (len(val), val)
		if type(val) == dict or isinstance(val, PersistentMapping) :
			text = _("dict(%i)%s") % (len(val.keys()), val.keys())
		if type(val) == set :
			text = _("set(%i)%s") % (len(val), val)
		if type(val) == tuple :
			text = _("tuple(%i)%s") % (len(val), val)
		x = rect.x + 1
		y = rect.y + 1
		dc.DrawText(text, x, y)

#	def GetBestSize(self, grid, attr, dc, row, col):
#		text = grid.GetCellValue(row, col)
#		dc.SetFont(attr.GetFont())
#		w, h = dc.GetTextExtent(text)
#		return wx.Size(w, h)

	def Clone(self):
		return ToStringRenderer()

###########################################################################
## Class CustomGrid
###########################################################################
class CustomGrid (gridlib.Grid ):
	def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
            size=wx.DefaultSize, style=wx.WANTS_CHARS):
		gridlib.Grid.__init__(self, parent, id, pos, size, style)
		self._raw_data = []
		self.colNums = 0
		self.activeEditor = None
		self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnCreateEditor)
		self.Bind(gridlib.EVT_GRID_EDITOR_SHOWN, self.OnStartEdit)
		self.Bind(gridlib.EVT_GRID_EDITOR_HIDDEN, self.OnStopEdit)

	def CreateGrid(self, numRows, numCols, selmode=gridlib.Grid.wxGridSelectCells):
		self.colNums = numCols
		self._raw_data = [[None]*self.colNums for i in range(numRows)]
		return gridlib.Grid.CreateGrid(self, numRows, numCols, selmode)

	def AppendRows(self, numRows=1, updateLabels=True):
		self._raw_data.extend([[None]*self.colNums for i in range(numRows)])
		return gridlib.Grid.AppendRows(self, numRows, updateLabels)

	def DeleteRows(self, pos=0, numRows=1, updateLabels=True):
		for ii in xrange(numRows):
			del self._raw_data[pos]	
		return gridlib.Grid.DeleteRows(self, pos, numRows, updateLabels)

	def SetCellValue(self, row, col, s):
		# save original value
		if len(self._raw_data) <= row:
			self._raw_data.extend([[None]*self.colNums for i in range(row - len(self._raw_data) + 1)])

		if len(self._raw_data[row]) <= col:
			self._raw_data[row].extend([None for i in range(col - len(self._raw_data[row]) + 1)])
		self._raw_data[row][col] = s
		gridlib.Grid.SetCellValue(self, row, col, str(s))

	def OnKeyDown(self, evt):
		if evt.GetKeyCode() != wx.WXK_RETURN:
			evt.Skip()
			return

	def GetCellRawValue(self, row, col):
		try:
			return self._raw_data[row][col]
		except IndexError:
			return None

	def OnStartEdit(self, evt):
		wx.GetApp().log("[Custom grid][dbg] begin edit: %s" % evt)
		evt.Skip()

	def OnStopEdit(self, evt):
		wx.GetApp().log("[Custom grid][dbg] finish edit %s" % evt)
		self.activeEditor = None
		evt.Skip()

	def OnCreateEditor(self, evt):
		wx.GetApp().log("[Custom grid][dbg] create editor %s" % evt)
		self.activeEditor = evt.Control
		evt.Skip()

	def FixOnClose(self):
		wx.GetApp().log("[Custom grid][dbg] fix-on-exit")
		pass
