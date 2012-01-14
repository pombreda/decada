# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        HtmlView
# Purpose:     Description for the HtmlView
#
# Author:      aabramov
#
# Created:     19.12.11
# Copyright:   (c) aabramov 2011
# Licence:     Private
#-------------------------------------------------------------------------------
import os
import wx
import  wx.html as  html
import wx.lib.agw.aui as aui
from Editra.src import ed_glob
from NbookPanel import NbookPanel
import gettext
_ = gettext.gettext

__author__ = 'aabramov'

###########################################################################
## Class HtmlView
###########################################################################
#################### __WXMSW__ ############################################
if wx.Platform == '__WXMSW__':
	import wx.lib.iewin as iewin
	class HtmlView(iewin.IEHtmlWindow):
		def __init__(self, parent):
			iewin.IEHtmlWindow.__init__(self, parent)
			self.parent = parent
			self.home_url = ''

		def TitleChange(self, this, Text):
			self.parent.SetHtmlTitle(Text)

		def LoadPage(self, uri):
			self.LoadUrl(uri)

		def Reload(self):
			self.Refresh(iewin.REFRESH_COMPLETELY)

		def GoHome(self):
			self.LoadUrl(self.home_url)

		def HistoryBack(self):
			self.GoBack()

		def HistoryForward(self):
			self.GoForward()

#################### __WXGTK__ ############################################
elif wx.Platform == '__WXGTK__':
	from webkit_gtk import WKHtmlWindow as HtmlWindow
	class HtmlView(HtmlWindow):
		def __init__(self, parent):
			HtmlWindow.__init__(self, parent)
			self.parent = parent
			self.home_url = ''
			wst = self.ctrl.get_settings()
			# need it for local search working
			wst.props.enable_file_access_from_file_uris = True

		def LoadPage(self, url):
			self.LoadUrl(url)

		def Reload(self):
			pass

		def GoHome(self):
			self.LoadUrl(self.home_url)

		def OnTitleChanged(self, title):
			self.parent.SetHtmlTitle(title)

#################### __WXMAC__ ############################################
else:
	class HtmlView(html.HtmlWindow):
		def __init__(self, parent, id, style):
			html.HtmlWindow.__init__(self, parent, id, style=style)
			self.parent = parent
			self.home_url = ''
			if "gtk2" in wx.PlatformInfo:
				self.SetStandardFonts()

		def OnSetTitle(self, title):
			self.parent.SetHtmlTitle(title)
			super(HtmlView, self).OnSetTitle(title)

		def Reload(self):
			pass

		def GoHome(self):
			self.LoadFile(self.home_url)

###########################################################################
## Class HtmlPanel
###########################################################################
class HtmlPanel(NbookPanel):
	ID_Location = wx.NewId()

	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		"""Initialize the HTML viewer"""
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "HtmlView"
		self.Title = _("Help viewer")
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_WEB), wx.ART_MENU, wx.Size(16, 16))

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.mtb = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_HORZ_LAYOUT)
		self.mtb.SetToolBitmapSize(wx.Size(16,16))
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_BACKWARD), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_BACKWARD, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Back"), _("Return to previous page"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_FORWARD), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_FORWARD, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Forward"), _("Go to the next page"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_REFRESH, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Refresh"), _("Reload current page"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_HOMEPAGE), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_HOME, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Home"), _("Go to the start page"), None)
		self.mtb.AddSpacer(1)
		self.Location = self.mtb.AddLabel(self.ID_Location, "about:blank")
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=5 )
		self.html = wx.Panel(self)

		bSizer.Add( self.html, proportion=1, flag=wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Bind(wx.EVT_MENU, self.OnBack, id=wx.ID_BACKWARD)
		self.Bind(wx.EVT_MENU, self.OnForward, id=wx.ID_FORWARD)
		self.Bind(wx.EVT_MENU, self.OnRefresh, id=wx.ID_REFRESH)
		self.Bind(wx.EVT_MENU, self.OnHome, id=wx.ID_HOME)
		self.Bind(wx.EVT_SHOW, self.OnShow)

	def _InitHtmlView(self):
		html = HtmlView(self)
		sz = self.GetSizer()
		sz.Replace(self.html, html)
		self.html.Destroy()
		self.html = html
		self.Layout()
		self.html.home_url = 'file://' + os.path.join(wx.GetApp().curr_dir, 'docs', 'index.html')
		self.html.GoHome()

	def OnShow(self, event):
		if event.IsShown():
			if not isinstance(self.html, HtmlView):
				self._InitHtmlView()
		pass

	def SetHtmlTitle(self, title):
		self.Location.SetLabel(title)
		self.mtb.Refresh()

	def OnBack(self, event):
		event.GetId()
		self.html.HistoryBack()

	def OnForward(self, event):
		event.GetId()
		self.html.HistoryForward()

	def OnRefresh(self, event):
		event.GetId()
		self.html.Reload()

	def OnHome(self, event):
		event.GetId()
		self.html.GoHome()
