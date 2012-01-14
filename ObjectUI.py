# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ObjjectUI
# Purpose:     Objects repository for the current world
#
# Author:      Stinger
#
# Created:     29.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import wx.combo
import gettext
from CustomGrid import CustomGrid, ToStringRenderer, ToStringEditor
import Deca
from Editra.src import ed_glob
from Deca.Object import DecaObject, DecaTemplate
_ = gettext.gettext

__author__ = 'stinger'

###########################################################################
## Class ObjDialog
###########################################################################
class ObjDialog ( wx.Dialog ):

	ID_SelectShape = wx.NewId()

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Object"), pos = wx.DefaultPosition,
							 size = wx.Size( 416,354 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

		self.Repository = None
		self.CurrentLayer = None
		self.TemplateName = ''

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bSizerTop = wx.BoxSizer( wx.HORIZONTAL )

		self.stName = wx.StaticText( self, wx.ID_ANY, _("Template:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stName.Wrap( -1 )
		bSizerTop.Add( self.stName, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5 )

		self.cbProto = wx.combo.BitmapComboBox( self, wx.ID_ANY )
		bSizerTop.Add( self.cbProto, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		self.chReflection = wx.CheckBox( self, wx.ID_ANY, _("reflection"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.chReflection.Enabled = False
		bSizerTop.Add( self.chReflection, proportion=0, flag=wx.ALL, border=5 )

		bSizer.Add( bSizerTop, proportion=0, flag=wx.EXPAND, border=0 )

		gbSizer = wx.GridBagSizer( 0, 0 )
		gbSizer.AddGrowableCol( 0 )
		gbSizer.AddGrowableRow( 2 )
		gbSizer.SetFlexibleDirection( wx.BOTH )
		gbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.attrGrid = CustomGrid( self, wx.ID_ANY, style=0 )

		# Grid
		self.attrGrid.CreateGrid( numRows=0, numCols=2 )
		self.attrGrid.EnableEditing( True )
		self.attrGrid.EnableGridLines( True )
		self.attrGrid.EnableDragGridSize( False )
		self.attrGrid.SetMargins( extraWidth=0, extraHeight=0 )

		# Columns
		self.attrGrid.SetColSize( 0, width=130 )
		self.attrGrid.SetColSize( 1, width=150 )
		self.attrGrid.EnableDragColMove( False )
		self.attrGrid.EnableDragColSize( True )
		self.attrGrid.SetColLabelSize( 30 )
		self.attrGrid.SetColLabelValue( 0, _("Attribute") )
		self.attrGrid.SetColLabelValue( 1, _("Value") )
		self.attrGrid.SetColLabelAlignment( horiz=wx.ALIGN_CENTRE, vert=wx.ALIGN_CENTRE )

		# Rows
		self.attrGrid.EnableDragRowSize( True )
		self.attrGrid.SetRowLabelSize( 20 )
		self.attrGrid.SetRowLabelAlignment( horiz=wx.ALIGN_CENTRE, vert=wx.ALIGN_CENTRE )

		# Label Appearance

		# Cell Defaults
		self.attrGrid.SetDefaultCellAlignment( horiz=wx.ALIGN_LEFT, vert=wx.ALIGN_TOP )
		gbSizer.Add( self.attrGrid, pos=wx.GBPosition( 0, 0 ), span=wx.GBSpan( 3, 1 ), flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2 )

		self.btnAdd = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnAdd, pos=wx.GBPosition( 0, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		self.btnDel = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REMOVE), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnDel, pos=wx.GBPosition( 1, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		self.btnSet = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_FONT), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnSet, pos=wx.GBPosition( 2, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		bSizer.Add( gbSizer, proportion=1, flag=wx.EXPAND|wx.BOTTOM, border=5 )

		bSizerBottom = wx.BoxSizer( wx.HORIZONTAL )

		self.stTitle = wx.StaticText( self, wx.ID_ANY, _("Title: %s (%s)") % ('None', 'None'), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTitle.Wrap( -1 )
		bSizerBottom.Add( self.stTitle, proportion=1, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5 )

		shapeSelChoices = [ "DefaultShape" ]
		shapeSelChoices.extend(Deca.world.GetShapes())
		self.shapeSel = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, shapeSelChoices, 0 )
		self.shapeSel.SetSelection( 0 )
		bSizerBottom.Add( self.shapeSel, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		bSizer.Add( bSizerBottom, proportion=0, flag=wx.EXPAND, border=0 )

		self.sdbSizer = wx.StdDialogButtonSizer()
		self.sdbButtonOK = wx.Button(self, wx.ID_OK)
		self.sdbSizer.AddButton(self.sdbButtonOK)
		self.sdbSizer.AddButton(wx.Button(self, wx.ID_CANCEL))
		self.sdbSizer.Realize()

		bSizer.Add( self.sdbSizer, proportion=0, flag=wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()
		self.Center( wx.BOTH )

		self.TitlePos = -1

		# Connect Events
		self.cbProto.Bind( wx.EVT_COMBOBOX, self.OnPrototype )
		self.btnAdd.Bind( wx.EVT_BUTTON, self.OnAdd )
		self.btnDel.Bind( wx.EVT_BUTTON, self.OnDel )
		self.btnSet.Bind( wx.EVT_BUTTON, self.OnSet )
		#self.sdbButtonOK.Bind( wx.EVT_BUTTON, self.OnOK )

	def SetEditMode(self, mode=True):
		self.stName.Enable(not mode)
		self.cbProto.Enable(not mode)
		self.chReflection.Enable(not mode)

	def AddChoice(self, img, name, code):
		self.cbProto.Append(name, bitmap=img, clientData=code)

	def EnableReflection(self, enable=True):
		self.chReflection.Enabled = enable
		if not enable:
			self.chReflection.SetValue(False)

	def AppendRows(self, num=1):
		last = self.attrGrid.GetNumberRows()
		self.attrGrid.AppendRows(num)
		pos = self.attrGrid.GetNumberRows()
		for r in range(last, pos):
			self.attrGrid.SetRowLabelValue(r, '')
			self.attrGrid.SetCellRenderer(row=r, col=1, renderer=ToStringRenderer())
			self.attrGrid.SetCellEditor(row=r, col=1, editor=ToStringEditor())

	def FixGrid(self):
		pos = self.attrGrid.GetNumberRows()
		self.attrGrid.DisableCellEditControl()
		#self.attrGrid.DeleteRows(pos=0, numRows=1)
		#for r in range(pos):
		#	self.attrGrid.SetCellEditor(row=r, col=1, editor=self.attrGrid.GetDefaultEditor())

	# Virtual event handlers, overide them in your derived class
	def OnPrototype( self, event ):
		event.GetId()
		x = self.attrGrid.GetNumberRows()
		if x > 0:
			self.attrGrid.DeleteRows(0, numRows=x)
		self.TitlePos = -1

		ttl = self.cbProto.GetSelection()
		if ttl != wx.NOT_FOUND:
			ttn = self.cbProto.GetString(ttl)
			ttl = self.cbProto.GetClientData(ttl)
			if ttl != '':
				# try to get template
				sample = self.Repository.GetTemplate(ttl)
				# try to get repo object
				if not sample : sample = self.Repository.GetObject(ttl)
				# try to get local object
				if not sample : sample = self.CurrentLayer.GetObject(ttl)
				# check reflection ability
				self.chReflection.Enabled = True
				if isinstance(sample, DecaTemplate):
					# can't reflect template
					self.chReflection.Value = False
					self.chReflection.Enabled = False
					self.TemplateName = ttn
				if isinstance(sample, DecaObject) and sample.IsReflection:
					# can't reflect reflection
					self.chReflection.Value = False
					self.chReflection.Enabled = False
					# reset TemplateName
					self.TemplateName = sample.TemplateName
				if sample is not None:
					self.AppendRows(len(sample.Attributes))
					x = 0
					for k,v in sample.Attributes.items():
						self.attrGrid.SetRowLabelValue(x, '')
						if k == sample.TitleAttr:
							self.attrGrid.SetRowLabelValue(x, '*')
							self.TitlePos = x
							self.stTitle.Label = _("Title attribute: %s") % k
						self.attrGrid.SetCellValue(row=x, col=0, s=k)
						self.attrGrid.SetCellValue(row=x, col=1, s=v)
						x += 1
					# end for each attribute
					if self.shapeSel.SetStringSelection(str(sample.Graphics)):
						self.shapeSel.SetSelection(0)
			# end if selected source
		# end if found

	def OnAdd( self, event ):
		event.GetId()
		self.AppendRows()

	def OnDel( self, event ):
		event.GetId()
		pos = self.attrGrid.GetSelectedRows()
		if len(pos) >= 0 :
			for x in pos:
				self.attrGrid.DeleteRows(x)
				if x == self.TitlePos:
					self.TitlePos = -1
					self.stTitle.Label = _("Title attribute: %s") % 'None'
				# end if Title
			# end for selected
		# end deletion

	def OnSet( self, event ):
		event.GetId()
		pos = self.attrGrid.GetSelectedRows()
		if not len(pos):
			cll = self.attrGrid.GetSelectedCells()
			if not len(cll):
				pos.append(self.attrGrid.GetGridCursorRow())
			for c in cll:
				pos.append(c.row)
		if len(pos) > 0 :
			if self.TitlePos > -1:
				self.attrGrid.SetRowLabelValue(self.TitlePos, '')
			self.TitlePos = pos[0]
			self.attrGrid.SetRowLabelValue(pos[0], '*')
			self.stTitle.Label = _("Title attribute: %s") % self.attrGrid.GetCellValue(pos[0], 0)
		# end set Title

	def GetShapeName(self):
		return self.shapeSel.GetStringSelection()

###########################################################################
## Support functions
###########################################################################
def CreateBrush(brush_tuple, def_brush):
	result = wx.Brush(def_brush.Colour, def_brush.Style)
	if len(brush_tuple) :		result.SetColour(wx.ColorRGB(brush_tuple[0]))
	if len(brush_tuple) > 1 :	result.Style = brush_tuple[1]
	return result

def SaveBrush(brush):
	result = (brush.Colour.GetRGB(), brush.Style)
	return result

def CreatePen(pen_tuple, def_pen):
	result = wx.Pen(def_pen.Colour, def_pen.Width, def_pen.Style)
	if len(pen_tuple) :		result.SetColour(wx.ColorRGB(pen_tuple[0]))
	if len(pen_tuple) > 1 :	result.Width = pen_tuple[1]
	if len(pen_tuple) > 2 :	result.Style = pen_tuple[2]
	return result

def SavePen(pen):
	result = (pen.Colour.GetRGB(), pen.Width, pen.Style)
	return result

###########################################################################
## Class ReflectObj
###########################################################################
class ReflectObjDlg ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Reflect Object"), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bSzView = wx.BoxSizer( wx.HORIZONTAL )

		self.stLabel = wx.StaticText( self, wx.ID_ANY, _("Reflect to layer: "), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLabel.Wrap( -1 )
		bSzView.Add( self.stLabel, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

		comboLayerChoices = [x for x in Deca.world.GetLayerList() if not x.startswith('@')]
		self.comboLayer = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, comboLayerChoices, 0 )
		bSzView.Add( self.comboLayer, proportion=0, flag=wx.ALL, border=5 )

		bSizer.Add( bSzView, proportion=1, flag=wx.EXPAND, border=5 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize()
		bSizer.Add( sdbSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=5 )

		self.SetSizer( bSizer )
		self.Layout()
		bSizer.Fit( self )

		self.Centre( wx.BOTH )
