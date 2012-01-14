# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ImgView
# Purpose:     Image library browser
#
# Author:      aabramov
#
# Created:     21.12.11
# Copyright:   (c) aabramov 2011
# Licence:     Private
#-------------------------------------------------------------------------------
import os
import wx
import wx.lib.agw.aui as aui
import Deca
#import wx.lib.agw.ultimatelistctrl as libul
from Editra.src import ed_glob
from NbookPanel import NbookPanel
import gettext
_ = gettext.gettext

__author__ = 'aabramov'

_THUMB_SIZE = 32

###########################################################################
## Class ImgImportDlg
###########################################################################
class ImgImportDlg ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Import Image"), pos = wx.DefaultPosition, size = wx.Size( 402,173 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bhSizer = wx.BoxSizer( wx.HORIZONTAL )

		self.bmp = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 100,100 ), wx.SUNKEN_BORDER )
		bhSizer.Add( self.bmp, 0, wx.ALL, 5 )

		gbSizer2 = wx.GridBagSizer( 0, 0 )
		gbSizer2.AddGrowableCol( 1 )
		gbSizer2.AddGrowableRow( 2 )
		gbSizer2.SetFlexibleDirection( wx.BOTH )
		gbSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.stTag = wx.StaticText( self, wx.ID_ANY, _("Image Tag:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTag.Wrap( -1 )
		gbSizer2.Add( self.stTag, wx.GBPosition( 0, 0 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.txtTag = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gbSizer2.Add( self.txtTag, wx.GBPosition( 0, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.stFile = wx.StaticText( self, wx.ID_ANY, _("Image source:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stFile.Wrap( -1 )
		gbSizer2.Add( self.stFile, wx.GBPosition( 1, 0 ), wx.GBSpan( 1, 1 ), wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.filePicker = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, _("Select a file"), u"*.*", wx.DefaultPosition, wx.DefaultSize, wx.FLP_DEFAULT_STYLE )
		gbSizer2.Add( self.filePicker, wx.GBPosition( 1, 1 ), wx.GBSpan( 1, 1 ), wx.ALL|wx.EXPAND, 5 )

		self.stInfo = wx.StaticText( self, wx.ID_ANY, _("Image info:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stInfo.Wrap( -1 )
		gbSizer2.Add( self.stInfo, wx.GBPosition( 2, 0 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		self.stImageInfo = wx.StaticText( self, wx.ID_ANY, _("1x1; 1 bytes"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stImageInfo.Wrap( -1 )
		gbSizer2.Add( self.stImageInfo, wx.GBPosition( 2, 1 ), wx.GBSpan( 1, 1 ), wx.ALL, 5 )

		bhSizer.Add( gbSizer2, 1, wx.EXPAND, 5 )

		bSizer.Add( bhSizer, 1, wx.EXPAND, 5 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize()
		bSizer.Add( sdbSizer, 0, wx.ALL|wx.EXPAND, 5 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.filePicker.Bind( wx.EVT_FILEPICKER_CHANGED, self.LoadFile )
		self.sdbSizerOK.Bind( wx.EVT_BUTTON, self.OnOk )

	# Virtual event handlers, overide them in your derived class
	def LoadFile( self, event ):
		img = wx.Bitmap(self.filePicker.GetPath())
		PREVIEW_SIZE = 100
		if img.IsOk():
			ix = img.GetWidth()
			iy = img.GetHeight()
			iz = os.stat(self.filePicker.GetPath()).st_size
			self.stImageInfo.SetLabel( _('%ix%i, %i bytes') % (ix,iy,iz))
			if ix > PREVIEW_SIZE or iy > PREVIEW_SIZE:
				sc = float(PREVIEW_SIZE) / float(max(ix, iy))
				sx = ix * sc
				sy = iy * sc
				scaled = img.ConvertToImage().Rescale(sx,sy,wx.IMAGE_QUALITY_HIGH)
				img = scaled.ConvertToBitmap()
				ix = img.GetWidth()
				iy = img.GetHeight()
			if ix < PREVIEW_SIZE or iy < PREVIEW_SIZE:
				bgi = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_EMPTY), wx.ART_MENU, wx.Size(PREVIEW_SIZE, PREVIEW_SIZE)).ConvertToImage()
				scaled = img.ConvertToImage()
				bgi.Paste(scaled, (PREVIEW_SIZE - ix)/2, (PREVIEW_SIZE - iy)/2)
				img = bgi.ConvertToBitmap()
			self.bmp.SetBitmap(img)
			self.bmp.Update()
			self.Refresh()
		event.Skip()

	def OnOk( self, event ):
		if self.txtTag.Value.strip() == "":
			wx.MessageBox(_("Enter image Tag!"), _("Sampo Image Library"), wx.OK|wx.ICON_WARNING)
			return
		event.Skip()

###########################################################################
## Class ImgPanel
###########################################################################
class ImgPanel(NbookPanel):
	ID_Location = wx.NewId()

	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		"""Initialize the HTML viewer"""
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "ImgView"
		self.Title = _("Image Library")
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_IMAGES), wx.ART_MENU, wx.Size(16, 16))

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.mtb = aui.AuiToolBar(self, -1, agwStyle=aui.AUI_TB_HORZ_LAYOUT)
		self.mtb.SetToolBitmapSize(wx.Size(16,16))
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_ADD, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add image"), _("Import image into the library"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_REMOVE), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_REMOVE, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Remove image"), _("Remove imeage from the library"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_REFRESH, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Refresh"), _("Reload library contents"), None)
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=5 )
		self.view = wx.ListCtrl( self, wx.ID_ANY, style=wx.LC_ICON|wx.LC_AUTOARRANGE )
		#self.view = libul.UltimateListCtrl( self, agwStyle=wx.LC_ICON|wx.LC_AUTOARRANGE| libul.ULC_AUTOARRANGE)
		#self.view.InsertColumn(0, heading="", width= 220)
		#self.view.InsertColumn(1, heading="", width= 220)

		bSizer.Add( self.view, proportion=1, flag=wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self.items = []

		self.Bind(wx.EVT_MENU, self.OnAddImage, id=wx.ID_ADD)
		self.Bind(wx.EVT_MENU, self.OnDelete, id=wx.ID_REMOVE)
		self.Bind(wx.EVT_MENU, self.UpdateView, id=wx.ID_REFRESH)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.view)

		wx.CallAfter(self.UpdateView)

	def UpdateColors(self, stm):
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.view.SetBackgroundColour(stm.GetDefaultBackColour())
		self.view.SetForegroundColour(stm.GetDefaultForeColour())
#		fnt = self.view.GetColumn(0).GetFont()
#		fnt.SetPixelSize(fnt.GetPixelSize() + (2,2))
#		self.view.GetColumn(0).SetFont(fnt)
#
#		fnt = self.view.GetColumn(1).GetFont()
#		fnt.SetPixelSize(fnt.GetPixelSize() - (2,2))
#		self.view.GetColumn(1).SetFont(fnt)

#		sm = stm.GetItemByName('comment')
#		cl = wx.Color()
#		cl.SetFromString(sm.back)
#		self.view.GetColumn(1).SetTextColour(cl)
		self.view.Refresh()
		pass

	def UpdateView(self, event=None):
		if event:
			event.GetId()
		# build file list
		fl = [f for f in os.listdir(Deca.world.PixmapsPath) if os.path.splitext(f)[1].lower() == '.png']
		imglist = wx.ImageList(_THUMB_SIZE, _THUMB_SIZE, initialCount=len(fl))
		self.items = []
		self.view.DeleteAllItems()
		for f in fl:
			title = os.path.splitext(f)[0]
			img = wx.Bitmap(os.path.join(Deca.world.PixmapsPath, f))
			ix = iy = iz =1
			if img.Ok():
				ix = img.GetWidth()
				iy = img.GetHeight()
				iz = os.stat(os.path.join(Deca.world.PixmapsPath, f)).st_size
				sc = float(_THUMB_SIZE) / float(max(ix, iy))
				sx = ix * sc
				sy = iy * sc
				scaled = img.ConvertToImage().Rescale(sx,sy,wx.IMAGE_QUALITY_HIGH)
				if sx != sy:
					bgi = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_EMPTY), wx.ART_MENU, wx.Size(_THUMB_SIZE, _THUMB_SIZE)).ConvertToImage()
					bgi.Paste(scaled, (_THUMB_SIZE - sx)/2, (_THUMB_SIZE - sy)/2)
					img = bgi.ConvertToBitmap()
				else:
					img = scaled.ConvertToBitmap()
			idx = imglist.Add(img)
			self.items.append((idx, title, _('%ix%i, %i bytes') % (ix,iy,iz)))
		self.view.AssignImageList(imglist, which=wx.IMAGE_LIST_NORMAL)
		idx = 0
		for i in self.items:
			self.view.InsertImageStringItem(idx, i[1], i[0])
			#self.view.SetStringItem(idx, col=1, label=i[2])
			idx += 1

	def OnItemSelected(self, event):
		if event.m_itemIndex >= 0 and event.m_itemIndex < len(self.items):
			wx.GetApp().TopWindow.SetStatus("%s: %s" % (self.items[event.m_itemIndex][1], self.items[event.m_itemIndex][2]))

		event.Skip()

	def OnAddImage(self, event):
		dlg = ImgImportDlg(self)
		if dlg.ShowModal() == wx.ID_OK:
			src = dlg.filePicker.GetPath()
			dst = os.path.join(Deca.world.PixmapsPath, dlg.txtTag.Value.strip() + '.png')
			img = wx.Bitmap(src)
			if img.IsOk():
				img.SaveFile(dst, wx.BITMAP_TYPE_PNG)
				self.UpdateView()
			else:
				wx.MessageBox(_("Can't read file %s!") % dlg.filePicker.GetPath(), _("Sampo Image Library"), wx.OK|wx.ICON_WARNING)
		# if dialog ok

	def OnDelete(self, event):
		event.GetId()
		if self.view.GetSelectedItemCount() > 0:
			if self.view.GetSelectedItemCount() == 1:
				msg = self.view.GetItemText(self.view.GetFirstSelected())
			else:
				msg = _("%i items") % self.view.GetSelectedItemCount()
			if wx.MessageBox(_("Are you sure to delete %s") % msg, _("Image Library"), wx.YES_NO|wx.ICON_QUESTION) == wx.ID_YES:
				idx = self.view.GetFirstSelected()
				while idx > -1:
					fn = self.view.GetItemText(idx)
					fn = os.path.join(Deca.world.PixmapsPath, fn + '.png')
					os.remove(fn)
					idx = self.view.GetNextSelected(idx)
				# all deleted
			self.UpdateView()
		pass