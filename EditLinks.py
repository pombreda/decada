# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        EditLinks
# Purpose:     Description for the EditLinks
#
# Author:      Stinger
#
# Created:     05.12.11
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import gettext
from CustomGrid import EditIterable
from Deca.Utility import Filter
from Editra.src import ed_glob

_ = gettext.gettext

__author__ = 'aabramov'

###########################################################################
## Class LinksDlg
###########################################################################
class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)

class LinksDlg ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Add links"), pos = wx.DefaultPosition, size = wx.Size( 350,220 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )
		self.Items = []

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.linksList = CheckListCtrl( self )
		self.linksList.InsertColumn(0, heading="From", width= 220)
		self.linksList.InsertColumn(1, heading="To", width= 200)

		bSizer.Add( self.linksList, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		self.cbDirect = wx.CheckBox( self, wx.ID_ANY, _("Directional links"), wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer.Add( self.cbDirect, proportion=0, flag=wx.EXPAND|wx.LEFT, border=5 )

		sdbSizer = wx.StdDialogButtonSizer()
		self.sdbSizerOK = wx.Button( self, wx.ID_OK )
		sdbSizer.AddButton( self.sdbSizerOK )
		self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
		sdbSizer.AddButton( self.sdbSizerCancel )
		sdbSizer.Realize()
		bSizer.Add( sdbSizer, proportion=0, flag=wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, border=5 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

	def AddItem(self, objFrom, objTo):
		item = ['', '']
		item[0] = objFrom.GetTitle()
		item[1] = objTo.GetTitle()
		self.linksList.Append(item)
		self.Items.append((objFrom, objTo))
		pass

###########################################################################
## Class EdtLinks
###########################################################################
class EdtLinks ( wx.Dialog ):
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Edit links"), pos = wx.DefaultPosition, size = wx.Size( 403,248 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )
		self.edtObject = None
		self.edtLayer = None
		self.links = []

		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		bSizerIn = wx.BoxSizer( wx.HORIZONTAL )

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_OK), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_CANCEL), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_ELEM_TYPE), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16,16)))

		self.linksList = wx.ListCtrl( self, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER )
		self.linksList.AssignImageList(imglist, which=wx.IMAGE_LIST_SMALL)
		self.linksList.InsertColumn(0, heading="From", width= 200)
		self.linksList.InsertColumn(1, heading="To", width= 200)
		bSizerIn.Add( self.linksList, 1, wx.ALL|wx.EXPAND, 2 )

		bSizerBtn = wx.BoxSizer( wx.VERTICAL )

		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16, 16))
		self.btnAdd = wx.BitmapButton( self, wx.ID_ANY, tbmp, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizerBtn.Add( self.btnAdd, 0, wx.ALL, 5 )

		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_REMOVE), wx.ART_MENU, wx.Size(16, 16))
		self.btnDel = wx.BitmapButton( self, wx.ID_ANY, tbmp, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizerBtn.Add( self.btnDel, 0, wx.ALL, 5 )

		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DOCPROP), wx.ART_MENU, wx.Size(16, 16))
		self.btnProps = wx.BitmapButton( self, wx.ID_ANY, tbmp, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		bSizerBtn.Add( self.btnProps, 0, wx.ALL, 5 )

		bSizerIn.Add( bSizerBtn, 0, wx.EXPAND, 0 )

		bSizer.Add( bSizerIn, 1, wx.EXPAND, 0 )

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

		self.sdbSizerOK.Bind(wx.EVT_BUTTON, self.OnOK)
		self.sdbSizerCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
		self.btnAdd.Bind(wx.EVT_BUTTON, self.OnAdd)
		self.btnDel.Bind(wx.EVT_BUTTON, self.OnDel)
		self.btnProps.Bind(wx.EVT_BUTTON, self.OnProps)

	def _GetLinkProps(self, lnk):
		lnk_props = {}
		for attr in lnk.__dict__.keys():
			if attr != 'StartObject' and attr != 'FinishObject':
				lnk_props[attr] = lnk.__dict__[attr]
		if 'Title' not in lnk_props.keys():
			lnk_props['Title'] = ''
		return lnk_props

	def SetEditObject(self, layer, obj):
		self.edtLayer = layer
		self.edtObject = obj
		# fill up dialog
		self.links = []
		links = layer.GetLinks(lambda ln: ln.StartObject == obj.ID or ln.FinishObject == obj.ID)
		for ln in links:
			self.links.append([ln, self._GetLinkProps(ln)])
			item = ['', '']
			item[0] = layer.GetObject(ln.StartObject).GetTitle()
			item[1] = layer.GetObject(ln.FinishObject).GetTitle()
			inum = self.linksList.Append(item)
			self.linksList.SetItemImage(inum, 0)

	def OnCancel(self, event):
		# discard newly created changes
		for itm in range(self.linksList.GetItemCount()):
			st = self.linksList.GetItem(itm).Image
			if st == 3: # new link
				self.edtLayer.RemoveLink(self.links[itm][0])
		event.Skip()

	def OnOK(self, event):
		# apply changes
		for itm in range(self.linksList.GetItemCount()):
			st = self.linksList.GetItem(itm).Image
			if st == 1: # deleted link
				self.edtLayer.RemoveLink(self.links[itm][0])
			elif st == 2: # edited link
				# remove deleted attrs
				lnk = self.links[itm][0]
				atr = self.links[itm][1]
				for attr in lnk.__dict__.keys():
					if attr != 'StartObject' and attr != 'FinishObject':
						if attr not in atr.keys():
							lnk.__delattr__(attr)
				# set edited attrs
				for attr in atr.keys():
					lnk.__setattr__(attr, atr[attr])
		event.Skip()

	def OnAdd(self, event):
		item = ['', '']
		if self.edtObject and self.edtLayer:
			item[0] = self.edtObject.GetTitle()
			item[1] = "ToDo: add link"
			inum = self.linksList.Append(item)
			self.linksList.SetItemImage(inum, 3)
		event.Skip()

	def OnDel(self, event):
		itm = self.linksList.GetFirstSelected()
		if itm > -1:
			if wx.MessageBox(_("Are you sure to remove link?"), _("Sampo Framework"), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
				self.linksList.SetItemImage(itm, 1)
		event.Skip()

	def OnProps(self, event):
		itm = self.linksList.GetFirstSelected()
		if itm > -1 and itm < len(self.links):
			dlg = EditIterable(self)
			dlg.SetData(self.links[itm][1])
			if dlg.ShowModal() == wx.ID_OK:
				# save link attributes
				self.links[itm][1] = dlg.GetData()
				# set modification marker
				self.linksList.SetItemImage(itm, 2)
		event.Skip()
