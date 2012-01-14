# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Settings
# Purpose:     Settings window
#
# Author:      Stinger
#
# Created:     18.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import wx.lib.agw.aui as aui
from Editra.src import eclib, ed_glob, ed_i18n
import Editra.src.util as util
import Editra.src.ed_msg as ed_msg
from Editra.src.profiler import Profile_Get, Profile_Set
import gettext
_ = gettext.gettext


class ScSettings(wx.Dialog):
	"""Settings window"""
	def __init__(self, parent, id_=wx.ID_ANY,
				 style=wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU):
		"""Initializes the preference panel
		@param parent: The parent window of this window
		@param id_: The id of this window
		"""
		super(ScSettings, self).__init__ (parent, id_,
							_("Sampo Preferences"),
							wx.DefaultPosition,
							wx.Size(400, 300),
							style)
		util.SetWindowIcon(self)
		self.parent = parent
		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.nbs = aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, aui.AUI_NB_DEFAULT_STYLE )
		self.gen = wx.Panel( self.nbs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gen_layout = wx.BoxSizer( wx.VERTICAL )

		gen_table = wx.FlexGridSizer( 2, 2, 0, 0 )
		gen_table.SetFlexibleDirection( wx.BOTH )
		gen_table.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.stLocale = wx.StaticText( self.gen, wx.ID_ANY, _("Locale settings:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stLocale.Wrap( -1 )
		gen_table.Add( self.stLocale, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		cbLanguageChoices = ['Default']
		self.cbLanguage = wx.Choice( self.gen, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cbLanguageChoices, 0 )
		self.cbLanguage.SetSelection( 0 )
		gen_table.Add( self.cbLanguage, 0, wx.ALL, 5 )

		gen_layout.Add( gen_table, 0, wx.EXPAND, 5 )

		self.cbSettings = wx.CheckBox( self.gen, wx.ID_ANY, _("Allow settings edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		gen_layout.Add( self.cbSettings, 0, wx.ALL, 5 )
		self.cbSettings.SetValue(Profile_Get('ALLOW_SETTINGS', 'bool', True))

		self.cbEngines = wx.CheckBox( self.gen, wx.ID_ANY, _("Allow engines edit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		gen_layout.Add( self.cbEngines, 0, wx.ALL, 5 )
		self.cbEngines.SetValue(Profile_Get('ALLOW_ENGINES', 'bool', True))

		self.cbConsole = wx.CheckBox( self.gen, wx.ID_ANY, _("Allow console view"), wx.DefaultPosition, wx.DefaultSize, 0 )
		gen_layout.Add( self.cbConsole, 0, wx.ALL, 5 )
		self.cbConsole.SetValue(Profile_Get('ALLOW_CONSOLE', 'bool', True))

		gen_layout.AddSpacer( ( 0, 5), 0, wx.EXPAND, 5 )

		self.cbConsole2 = wx.CheckBox( self.gen, wx.ID_ANY, _("Show console at start-up"), wx.DefaultPosition, wx.DefaultSize, 0 )
		gen_layout.Add( self.cbConsole2, 0, wx.LEFT, 15 )
		if self.cbConsole.IsChecked() :
			self.cbConsole2.SetValue(Profile_Get('SHOW_CONSOLE', 'bool', True))
		else:
			self.cbConsole2.SetValue(False)
			self.cbConsole2.Disable()

		gen_layout.AddSpacer( ( 0, 5), 0, wx.EXPAND, 5 )

		self.gen.SetSizer( gen_layout )
		self.gen.Layout()
		gen_layout.Fit( self.gen )
		self.nbs.AddPage( self.gen, _("General"), True, wx.NullBitmap )

		self.app = wx.Panel( self.nbs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		app_layout = wx.FlexGridSizer( 16, 2, 5, 5 )
		app_layout.SetFlexibleDirection( wx.BOTH )
		app_layout.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.st1 = wx.StaticText( self.app, wx.ID_ANY, _("Color Scheme:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.st1.Wrap( -1 )
		app_layout.Add( self.st1, 0, wx.ALL, 5 )

		colorsChoices = sorted(util.GetResourceFiles(u'styles', True, True, title=False))
		self.colors = wx.Choice( self.app, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, colorsChoices, 0 )
		self.colors.SetStringSelection( Profile_Get('SYNTHEME', 'str', 'default') )
		app_layout.Add( self.colors, 0, wx.ALL, 5 )

		self.st2 = wx.StaticText( self.app, wx.ID_ANY, _("Icons:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.st2.Wrap( -1 )
		app_layout.Add( self.st2, 0, wx.ALL, 5 )

		from Editra.src.ed_theme import BitmapProvider
		iconsChoices = ['Default']
		iconsChoices.extend(BitmapProvider(wx.GetApp().GetPluginManager()).GetThemes())
		self.icons = wx.Choice( self.app, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, iconsChoices, 0 )
		self.icons.SetSelection( 0 )
		app_layout.Add( self.icons, 0, wx.ALL, 5 )

		self.st3 = wx.StaticText( self.app, wx.ID_ANY, _("Layout:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.st3.Wrap( -1 )
		app_layout.Add( self.st3, 0, wx.ALL, 5 )

		self.cbWinSize = wx.CheckBox( self.app, wx.ID_ANY, _("Remember Window Size on Exit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		app_layout.Add( self.cbWinSize, 0, wx.ALL, 5 )

		app_layout.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.cbWinPos = wx.CheckBox( self.app, wx.ID_ANY, _("Remember Window Position on Exit"), wx.DefaultPosition, wx.DefaultSize, 0 )
		app_layout.Add( self.cbWinPos, 0, wx.ALL, 5 )

		self.app.SetSizer( app_layout )
		self.app.Layout()
		app_layout.Fit( self.app )
		self.nbs.AddPage( self.app, _("Appearance"), False, wx.NullBitmap )

		self.edt = wx.Panel( self.nbs, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		edt_layout = wx.FlexGridSizer( 2, 2, 0, 0 )
		edt_layout.SetFlexibleDirection( wx.BOTH )
		edt_layout.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.sc5 = wx.StaticText( self.edt, wx.ID_ANY, _("Editor font:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.sc5.Wrap( -1 )
		edt_layout.Add( self.sc5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		fnt = Profile_Get('FONT1', 'font', wx.NORMAL_FONT)
		self.fpick = eclib.PyFontPicker(self.edt, ed_glob.ID_FONT, fnt)
		self.fpick.SetToolTipString(_("Main display font for various UI components"))

		edt_layout.Add( self.fpick, 1, wx.EXPAND, 5 )

		self.cbEdge = wx.CheckBox( self.edt, ed_glob.ID_SHOW_EDGE, _("Edge guide"), wx.DefaultPosition, wx.DefaultSize, 0 )
		edt_layout.Add( self.cbEdge, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		self.cbEdge.SetValue(Profile_Get('SHOW_EDGE'))

		self.spinEdge = wx.SpinCtrl( self.edt, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 10, 200, 80 )
		edt_layout.Add( self.spinEdge, 0, wx.ALL, 5 )
		self.spinEdge.SetValue(Profile_Get('EDGE', 'int', 80))

		self.cbFolding = wx.CheckBox( self.edt, ed_glob.ID_FOLDING, _("Code folding"), wx.DefaultPosition, wx.DefaultSize, 0 )
		edt_layout.Add( self.cbFolding, 0, wx.ALL, 5 )
		self.cbFolding.SetValue(Profile_Get('CODE_FOLD'))

		edt_layout.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.cbNumbers = wx.CheckBox( self.edt, ed_glob.ID_SHOW_LN, _("Line numbers"), wx.DefaultPosition, wx.DefaultSize, 0 )
		edt_layout.Add( self.cbNumbers, 0, wx.ALL, 5 )
		self.cbNumbers.SetValue(Profile_Get('SHOW_LN'))

		edt_layout.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.stTabsWidth = wx.StaticText( self.edt, wx.ID_ANY, _("Tabs Width:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTabsWidth.Wrap( -1 )
		edt_layout.Add( self.stTabsWidth, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.spinTabs = wx.SpinCtrl( self.edt, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 20, 8 )
		edt_layout.Add( self.spinTabs, 0, wx.ALL, 5 )
		self.spinTabs.SetValue(Profile_Get('TABWIDTH', 'int', 8))

		self.stIndent = wx.StaticText( self.edt, wx.ID_ANY, _("Indent Width:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stIndent.Wrap( -1 )
		edt_layout.Add( self.stIndent, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.spinIndent = wx.SpinCtrl( self.edt, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 20, 4 )
		edt_layout.Add( self.spinIndent, 0, wx.ALL, 5 )
		self.spinIndent.SetValue(Profile_Get('INDENTWIDTH', 'int', 4))

		self.cbUseTabs = wx.CheckBox( self.edt, ed_glob.ID_PREF_TABS, _("Use Tabs"), wx.DefaultPosition, wx.DefaultSize, 0 )
		edt_layout.Add( self.cbUseTabs, 0, wx.ALL, 5 )
		self.cbUseTabs.SetValue(Profile_Get('USETABS', 'bool', False))

		self.edt.SetSizer( edt_layout )
		self.edt.Layout()
		edt_layout.Fit( self.edt )
		self.nbs.AddPage( self.edt, _("Editor"), False, wx.NullBitmap )

		bSizer.Add( self.nbs, 1, wx.EXPAND |wx.ALL, 0 )

		sdbSizer = wx.StdDialogButtonSizer()
		sdbSizer.AddButton(wx.Button(self, wx.ID_OK))
		#sdbSizer.AddButton(wx.Button(self, wx.ID_CANCEL))
		sdbSizer.Realize()

		bSizer.Add( sdbSizer, 0, wx.EXPAND |wx.ALL, 2 )

		self.SetSizer( bSizer )
		self.Layout()

		# Connect Events
		self.cbLanguage.Bind(wx.EVT_COMBOBOX, self.OnLangChoice)
		self.cbSettings.Bind( wx.EVT_CHECKBOX, self.OnSettings )
		self.cbEngines.Bind( wx.EVT_CHECKBOX, self.OnEngines )
		self.cbConsole.Bind( wx.EVT_CHECKBOX, self.OnConsole )
		self.cbConsole2.Bind( wx.EVT_CHECKBOX, self.OnConsole2 )

		self.colors.Bind( wx.EVT_CHOICE, self.OnColorChange )
		self.icons.Bind( wx.EVT_CHOICE, self.OnIconsChange )
		self.Bind(eclib.EVT_FONT_CHANGED, self.OnSetFont)
		self.cbEdge.Bind( wx.EVT_CHECKBOX, self.OnCheck )
		self.cbFolding.Bind( wx.EVT_CHECKBOX, self.OnCheck )
		self.cbNumbers.Bind( wx.EVT_CHECKBOX, self.OnCheck )
		self.cbUseTabs.Bind( wx.EVT_CHECKBOX, self.OnCheck )

		self.spinEdge.Bind( wx.EVT_SPINCTRL, self.OnEdgeUpd )
		self.spinTabs.Bind( wx.EVT_SPINCTRL, self.OnTabsUpd )
		self.spinIndent.Bind( wx.EVT_SPINCTRL, self.OnIndentUpd )

	def __del__( self ):
		# Disconnect Events
		#self.btnSetFont.Unbind( wx.EVT_BUTTON, None )
		pass

	# Virtual event handlers, overide them in your derived class
	def OnColorChange( self, event ):
		val = self.colors.GetStringSelection()
		self.parent.UpdateColors(val)
		Profile_Set('SYNTHEME', val)

	def OnIconsChange( self, event ):
		val = self.colors.GetStringSelection()
		Profile_Set('ICONS', val)
		wx.GetApp().ReloadArtProvider()
		ed_msg.PostMessage(ed_msg.EDMSG_THEME_CHANGED, True)

	def OnLangChoice(self, event):
		e_id = event.GetId()
		e_obj = event.GetEventObject()
		if e_id == ed_glob.ID_PREF_LANG:
			Profile_Set(ed_glob.ID_2_PROF[e_id], e_obj.GetValue())
		else:
			event.Skip()

	def OnSettings(self, evt):
		evt.GetId()
		Profile_Set('ALLOW_SETTINGS', self.cbSettings.GetValue())
		pass

	def OnEngines(self, evt):
		evt.GetId()
		Profile_Set('ALLOW_ENGINES', self.cbEngines.GetValue())
		pass

	def OnConsole(self, evt):
		evt.GetId()
		Profile_Set('ALLOW_CONSOLE', self.cbConsole.GetValue())
		if self.cbConsole.IsChecked() :
			self.cbConsole2.SetValue(Profile_Get('SHOW_CONSOLE', 'bool', True))
			self.cbConsole2.Enable()
		else:
			Profile_Set('SHOW_CONSOLE', False)
			self.cbConsole2.SetValue(False)
			self.cbConsole2.Disable()
		pass

	def OnConsole2(self, evt):
		evt.GetId()
		Profile_Set('SHOW_CONSOLE', self.cbConsole2.GetValue())
		pass

	def OnSetFont( self, event ):
		e_id = event.GetId()
		if e_id == ed_glob.ID_FONT:
			font = event.GetValue()
			if not isinstance(font, wx.Font) or font.IsNull():
				return
			Profile_Set('FONT1', font, 'font')
#			for main in wx.GetApp().GetMainWindows():
#				for stc in main.nb.GetTextControls():
#					stc.SetStyleFont(font, e_id == DocGenPanel.ID_FONT_PICKER)
#					stc.UpdateAllStyles()
		else:
			event.Skip()

	def OnCheck( self, event ):
		e_id = event.GetId()
		if e_id in (ed_glob.ID_SHOW_EDGE, ed_glob.ID_SHOW_LN,
					ed_glob.ID_FOLDING, ed_glob.ID_PREF_TABS):

			e_val = event.EventObject.GetValue()

			# Update Profile
			Profile_Set(ed_glob.ID_2_PROF[e_id], e_val)

			# Make ui adjustments
			meth = None
			args = list()
			if e_id == ed_glob.ID_SHOW_EDGE:
				self.spinEdge.Enable(e_val)
		else:
			event.Skip()

	def OnEdgeUpd( self, event ):
		Profile_Set('EDGE', self.spinEdge.GetValue())
		event.Skip()

	def OnTabsUpd( self, event ):
		Profile_Set('TABWIDTH', self.spinTabs.GetValue())
		event.Skip()

	def OnIndentUpd( self, event ):
		Profile_Set('INDENTWIDTH', self.spinIndent.GetValue())
		event.Skip()
