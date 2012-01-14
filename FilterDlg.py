# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ObjRepo
# Purpose:     Objects repository for the current world
#
# Author:      Stinger
#
# Created:     18.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import gettext
import Deca
from Editra.src import ed_stc

_ = gettext.gettext

__author__ = 'stinger'

class FilterBuff ( ed_stc.EditraStc ):
	modeText = 0
	modeObjects = 1
	modeLinks = 2
	
	def __init__(self, parent, id_,
				 pos=wx.DefaultPosition, size=wx.DefaultSize,
				 style=0, use_dt=True):
		ed_stc.EditraStc.__init__(self, parent, id_, pos, size, style, use_dt)
		self._mode = self.modeText

	def GetText(self):
		if self._mode == self.modeObjects :
			res = "import uuid\n"
			res += "import Deca\n"
			res += "oid = uuid.uuid4('')\n"
			res += "obj = Deca.Object()\n"
		elif self._mode == self.modeLinks :
			res = "import uuid\n"
			res += "import Deca\n"
			res += "link = Deca.Link()\n"
		else:
			res = ''
		res += super(ed_stc.EditraStc, self).GetText()
		return res

	def SetMode(self, mode):
		self._mode = mode

	def GetClearText(self):
		return super(ed_stc.EditraStc, self).GetText()

class LayerFilterDlg ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Layer filters"), pos = wx.DefaultPosition, size = wx.Size( 428,343 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )
		self.Items = []

		bSizer = wx.BoxSizer( wx.VERTICAL )

		fgSizer = wx.FlexGridSizer( 4, 2, 0, 0 )
		fgSizer.AddGrowableCol( 1 )
		fgSizer.AddGrowableRow( 1 )
		fgSizer.AddGrowableRow( 3 )
		fgSizer.SetFlexibleDirection( wx.BOTH )
		fgSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		fgSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.stObjLabel = wx.StaticText( self, wx.ID_ANY, _("Objects filter"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stObjLabel.Wrap( -1 )
		self.stObjLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		fgSizer.Add( self.stObjLabel, proportion=0, flag=wx.ALL, border=2 )

		self.stObj = wx.StaticText( self, wx.ID_ANY, _("lambda oid, obj:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stObj.Wrap( -1 )
		fgSizer.Add( self.stObj, proportion=0, flag=wx.ALL, border=2 )

		self.LambdaObj = FilterBuff(self, wx.ID_ANY)
		self.LambdaObj.ConfigureLexer('py')
		self.LambdaObj.ConfigureAutoComp()
		self.LambdaObj.EnableLineNumbers(False)
		self.LambdaObj.SetMode(FilterBuff.modeObjects)
		fgSizer.Add( self.LambdaObj, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		fgSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.stLinkLabel = wx.StaticText( self, wx.ID_ANY, _("Links filter"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLinkLabel.Wrap( -1 )
		self.stLinkLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		fgSizer.Add( self.stLinkLabel, proportion=0, flag=wx.ALL, border=2 )

		self.stLinks = wx.StaticText( self, wx.ID_ANY, _("lambda link:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLinks.Wrap( -1 )
		fgSizer.Add( self.stLinks, proportion=1, flag=wx.ALL, border=2 )

		self.LambdaLnk = FilterBuff(self, wx.ID_ANY)
		self.LambdaLnk.ConfigureLexer('py')
		self.LambdaLnk.ConfigureAutoComp()
		self.LambdaLnk.EnableLineNumbers(False)
		self.LambdaLnk.SetMode(FilterBuff.modeLinks)
		fgSizer.Add( self.LambdaLnk, proportion=0, flag=wx.ALL|wx.EXPAND, border=2 )

		bSizer.Add( fgSizer, proportion=1, flag=wx.EXPAND, border=2 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer1Help = wx.Button( self, wx.ID_HELP )
		sdbSizer.AddButton( sdbSizer1Help )
		sdbSizer.Realize()
		bSizer.Add( sdbSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=2 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

class ReflectionFilterDlg ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Layer filters"), pos = wx.DefaultPosition, size = wx.Size( 428,343 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )
		self.Items = []

		bSizer = wx.BoxSizer( wx.VERTICAL )

		fgSizer = wx.FlexGridSizer( 4, 2, 0, 0 )
		fgSizer.AddGrowableCol( 1 )
		fgSizer.AddGrowableRow( 2 )
		fgSizer.AddGrowableRow( 4 )
		fgSizer.SetFlexibleDirection( wx.BOTH )
		fgSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.stLayer = wx.StaticText( self, wx.ID_ANY, _("Reflect to layer: "), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLayer.Wrap( -1 )
		fgSizer.Add( self.stLayer, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2 )

		bsz = wx.BoxSizer( wx.HORIZONTAL )

		comboLayerChoices = [x for x in Deca.world.GetLayerList() if not x.startswith('@')]
		self.comboLayer = wx.ComboBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, comboLayerChoices, 0 )
		bsz.Add( self.comboLayer, proportion=0, flag=wx.ALL, border=2 )

		self.chClear = wx.CheckBox( self, wx.ID_ANY, _("Clear layer before reflection"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bsz.Add( self.chClear, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=2 )

		fgSizer.Add( bsz, proportion=0, flag=wx.EXPAND, border=2 )

		fgSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.stObjLabel = wx.StaticText( self, wx.ID_ANY, _("Objects filter"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stObjLabel.Wrap( -1 )
		self.stObjLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		fgSizer.Add( self.stObjLabel, proportion=0, flag=wx.ALL, border=2 )

		self.stObj = wx.StaticText( self, wx.ID_ANY, _("lambda oid, obj:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stObj.Wrap( -1 )
		fgSizer.Add( self.stObj, proportion=0, flag=wx.ALL, border=2 )

		self.LambdaObj = FilterBuff(self, wx.ID_ANY)
		self.LambdaObj.ConfigureLexer('py')
		self.LambdaObj.ConfigureAutoComp()
		self.LambdaObj.EnableLineNumbers(False)
		self.LambdaObj.SetMode(FilterBuff.modeObjects)
		fgSizer.Add( self.LambdaObj, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		fgSizer.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.stLinkLabel = wx.StaticText( self, wx.ID_ANY, _("Links filter"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLinkLabel.Wrap( -1 )
		self.stLinkLabel.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )

		fgSizer.Add( self.stLinkLabel, proportion=0, flag=wx.ALL, border=2 )

		self.stLinks = wx.StaticText( self, wx.ID_ANY, _("lambda link:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLinks.Wrap( -1 )
		fgSizer.Add( self.stLinks, proportion=1, flag=wx.ALL, border=2 )

		self.LambdaLnk = FilterBuff(self, wx.ID_ANY)
		self.LambdaLnk.ConfigureLexer('py')
		self.LambdaLnk.ConfigureAutoComp()
		self.LambdaLnk.EnableLineNumbers(False)
		self.LambdaLnk.SetMode(FilterBuff.modeLinks)
		fgSizer.Add( self.LambdaLnk, proportion=0, flag=wx.ALL|wx.EXPAND, border=2 )

		bSizer.Add( fgSizer, proportion=1, flag=wx.EXPAND, border=2 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer1Help = wx.Button( self, wx.ID_HELP )
		sdbSizer.AddButton( sdbSizer1Help )
		sdbSizer.Realize()
		bSizer.Add( sdbSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=2 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )
