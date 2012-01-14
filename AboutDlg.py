# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        SamPy
# Purpose:     Main module of the Sampo framework
#
# Author:      Stinger
#
# Created:     15.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import os

import gettext
_ = gettext.gettext

###########################################################################
## Class AboutBox
###########################################################################

class AboutBox ( wx.Dialog ):
	"""Dialog box to show "About" window"""
	version_label = """Sampo Framework
Version 1.0
About authors
"""
	info_label = """Credits:
Editra
ZODB
wxPython (wxWidgets)
wxGtkWebKit - Richard Prescott
"""

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("About Sampo"), pos = wx.DefaultPosition, size = wx.Size( 430,300 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.m_panel6 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 133,-1 ), wx.TAB_TRAVERSAL )
		bSizerImage = wx.BoxSizer( wx.VERTICAL )

		path = os.path.join(wx.GetApp().curr_dir, "pixmaps", "About.png")
		self.splash = wx.StaticBitmap( self.m_panel6, wx.ID_ANY, wx.Bitmap( path, wx.BITMAP_TYPE_ANY ), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerImage.Add( self.splash, 0, wx.ALL, 5 )

		self.m_panel6.SetSizer( bSizerImage )
		self.m_panel6.Layout()
		bSizer.Add( self.m_panel6, 0, wx.EXPAND |wx.ALL, 0 )

		bSizerData = wx.BoxSizer( wx.VERTICAL )

		self.mstVersion = wx.StaticText( self, wx.ID_ANY, self.version_label, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mstVersion.Wrap( -1 )
		bSizerData.Add( self.mstVersion, 1, wx.TOP|wx.EXPAND, 5 )

		self.mtCredits = wx.TextCtrl( self, wx.ID_ANY, self.info_label, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.TE_READONLY|wx.SUNKEN_BORDER )
		bSizerData.Add( self.mtCredits, 1, wx.ALL|wx.EXPAND, 0 )

		self.m_panel8 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer17.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnOk = wx.Button( self.m_panel8, wx.ID_ANY, _("OK"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.btnOk, 0, wx.ALL, 5 )

		self.m_panel8.SetSizer( bSizer17 )
		self.m_panel8.Layout()
		bSizer17.Fit( self.m_panel8 )
		bSizerData.Add( self.m_panel8, 0, wx.EXPAND |wx.ALL, 0 )

		bSizer.Add( bSizerData, 1, wx.EXPAND, 5 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnOk.Bind( wx.EVT_BUTTON, self.OnOK )
		self.mtCredits.SetSelection(0, 0)

	def __del__( self ):
		# Disconnect Events
		#self.btnOk.Unbind( wx.EVT_BUTTON, None )
		pass


	# Virtual event handlers, overide them in your derived class
	def OnOK( self, event ):
		self.Close()
