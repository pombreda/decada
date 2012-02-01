# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        RepoView
# Purpose:     Interface HG repository. History view and operations
#
# Copyright:   (c) Triplika 2012
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import wx.lib.agw.aui as aui
from datetime import datetime
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin, CheckListCtrlMixin
import Deca
from NbookPanel import *
from ObjectUI import UserPassDlg
from Editra.src.profiler import Profile_Set
import HgCommon
import gettext
_ = gettext.gettext

###########################################################################
## List controls
###########################################################################
class AutoListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		ListCtrlAutoWidthMixin.__init__(self)

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
		ListCtrlAutoWidthMixin.__init__(self)

###########################################################################
## Class RepoView
###########################################################################
class RepoView(NbookPanel):
	"""Notebook panel for Repository View and operations"""
	ID_Commit = wx.NewId()
	ID_Update = wx.NewId()
	ID_Push = wx.NewId()
	ID_Pull = wx.NewId()
	ID_Options = wx.NewId()
	ID_RepoMode = wx.NewId()
	ID_Refresh = wx.NewId()

	colors = [
		[ # light background
			wx.ColorRGB(0x80ff80), # patch line background
			wx.ColorRGB(0x800080), # patch line text
			wx.ColorRGB(0x008000), # added line text
			wx.ColorRGB(0x000080)  # removed line text
		],
		[  # dark background
			wx.ColorRGB(0x40B040), # patch line background
			wx.ColorRGB(0xD000D0), # patch line text
			wx.ColorRGB(0x00D000), # added line text
			wx.ColorRGB(0x0000D0)  # removed line text
		]
	]

	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
	             size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "RepoView"
		self.Title = _('Repository')
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_REPOSITORY), wx.ART_MENU, wx.Size(16, 16))
		self.log = wx.GetApp().GetLog()

		self._localBmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_COMPUTER), wx.ART_MENU, wx.Size(16, 16))
		self._localBmpGr = self._localBmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self._remoteBmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_WEB), wx.ART_MENU, wx.Size(16, 16))
		self._remoteBmpGr = self._remoteBmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self._repoModeLocal = True

		bSizer = wx.BoxSizer( wx.VERTICAL )
		self.mtb = aui.AuiToolBar(self, -1)
		self.mtb.SetToolBitmapSize(wx.Size(16,16))
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU, wx.Size(16, 16))
		gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self.mtb.AddTool( self.ID_Commit, '', tbmp, gbmp,
			wx.ITEM_NORMAL, _('Commit'), _('Store version locally'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DOWN), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool( self.ID_Update, '', tbmp, tbmp,
			wx.ITEM_NORMAL, _('Update'), _('Reload revision from repository'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_PUSH), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool( self.ID_Push, '', tbmp, tbmp,
			wx.ITEM_NORMAL, _('Push'), _('Save version to remote repository'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_PULL), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool( self.ID_Pull, '', tbmp, tbmp,
			wx.ITEM_NORMAL, _('Synchronize'), _('Update from remote repository'), None)
		self.mtb.AddSeparator()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool( self.ID_Options, '', tbmp, tbmp,
			wx.ITEM_NORMAL, _('Repository options'), _('Settings for the repository'), None)
		self.mtb.AddTool( self.ID_RepoMode, '', self._localBmp, self._localBmpGr,
			wx.ITEM_NORMAL, _('Local history'), _('Switch to remote repository'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool( self.ID_Refresh, '', tbmp, tbmp,
			wx.ITEM_NORMAL, _('Refresh view'), _('Update history information'), None)
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=0 )

		self.vsplit = wx.SplitterWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.vsplit.Bind( wx.EVT_IDLE, self.vsplitOnIdle )
		
		self.top_pane = wx.Panel( self.vsplit, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		topSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.repoHistory = AutoListCtrl( self.top_pane)
		self.repoHistory.setResizeColumn(4)
		topSizer.Add( self.repoHistory, proportion=1, flag=wx.ALL|wx.EXPAND, border=1 )
		self.repoHistory.InsertColumn(col=0, heading=_('Graph'), width=20)
		self.repoHistory.InsertColumn(col=1, heading=_('Rev'), width=40)
		self.repoHistory.InsertColumn(col=2, heading=_('Branch'), width=60)
		self.repoHistory.InsertColumn(col=3, heading=_('Description'), width=20)
		self.repoHistory.InsertColumn(col=4, heading=_('Author'), width=60)
		self.repoHistory.InsertColumn(col=5, heading=_('Age'), width=60)
		self.repoHistory.InsertColumn(col=6, heading=_('Tags'), width=60)

		self.top_pane.SetSizer( topSizer )
		self.top_pane.Layout()
		topSizer.Fit( self.top_pane )
		self.bottom_pane = wx.Panel( self.vsplit, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bottomSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.hsplit = wx.SplitterWindow( self.bottom_pane, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.SP_3D )
		self.hsplit.Bind( wx.EVT_IDLE, self.hsplitOnIdle )
		
		self.left_pane = wx.Panel( self.hsplit, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		leftSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.fileList = CheckListCtrl( self.left_pane )
		leftSizer.Add( self.fileList, proportion=1, flag=wx.ALL|wx.EXPAND, border=1 )
		self.fileList.InsertColumn(col=0, heading=_('*'), width=20)
		self.fileList.InsertColumn(col=1, heading=_('File'))

		self.left_pane.SetSizer( leftSizer )
		self.left_pane.Layout()
		leftSizer.Fit( self.left_pane )
		self.right_pane = wx.Panel( self.hsplit, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		rightSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.stTitle = wx.StaticText( self.right_pane, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTitle.Wrap( -1 )
		rightSizer.Add( self.stTitle, proportion=0, flag=wx.ALL, border=5 )
		
		self.txtDiff = wx.ListCtrl( self.right_pane, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_NO_HEADER|wx.LC_NO_SORT_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.txtDiff.InsertColumn(col=0, heading=_('Text'))
		self.txtDiff.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 76, 90, 90, False, wx.EmptyString ) )
		self.txtwid = 0
		self.color_scheme = 0
		rightSizer.Add( self.txtDiff, proportion=1, flag=wx.EXPAND |wx.ALL, border=5 )
		
		self.right_pane.SetSizer( rightSizer )
		self.right_pane.Layout()
		rightSizer.Fit( self.right_pane )
		self.hsplit.SplitVertically( self.left_pane, window2=self.right_pane, sashPosition=180 )
		bottomSizer.Add( self.hsplit, proportion=1, flag=wx.EXPAND, border=5 )
		
		self.bottom_pane.SetSizer( bottomSizer )
		self.bottom_pane.Layout()
		bottomSizer.Fit( self.bottom_pane )
		self.vsplit.SplitHorizontally( self.top_pane, window2=self.bottom_pane, sashPosition=100 )
		bSizer.Add( self.vsplit, proportion=1, flag=wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Bind( wx.EVT_IDLE, self.OnIdle )
		self.repoHistory.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnRevSelected )
		self.fileList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnFileSelected )
		self.txtDiff.Bind( wx.EVT_SIZE, self.OnTxtResize)
		self.Bind( wx.EVT_MENU, self.OnCommit, id=self.ID_Commit )
		self.Bind( wx.EVT_MENU, self.OnPush, id=self.ID_Push )
		self.Bind( wx.EVT_MENU, self.OnPull, id=self.ID_Pull )
		self.Bind( wx.EVT_MENU, self.OnChangeLocation, id=self.ID_RepoMode )
		self.Bind( wx.EVT_MENU, self.OnRefresh, id=self.ID_Refresh )

		self._wasChanged = not Deca.world.HgRepository.IsWdChanged
		wx.CallAfter(self.FillRepoView)

	def UpdateColors(self, stm):
		self.style = stm.GetCurrentStyleSetName()
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.repoHistory.SetBackgroundColour(stm.GetDefaultBackColour())
		self.repoHistory.SetForegroundColour(stm.GetDefaultForeColour())
		self.fileList.SetBackgroundColour(stm.GetDefaultBackColour())
		self.fileList.SetForegroundColour(stm.GetDefaultForeColour())
		self.txtDiff.SetBackgroundColour(stm.GetDefaultBackColour())
		self.txtDiff.SetForegroundColour(stm.GetDefaultForeColour())
		fnt = self.txtDiff.GetFont()
		sz = stm.GetDefaultFont().GetPixelSize()
		fnt.SetPixelSize((sz[0] - 1, sz[1]))
		self.txtDiff.SetFont(fnt)
		bg = stm.GetDefaultBackColour()
		bg = (bg.red * 30 / 100) + (bg.green * 59 / 100) + (bg.blue * 11 / 100)
		if bg > 0x80:
			self.color_scheme = 0 # light background
		else :
			self.color_scheme = 1 # dark background
		self.Refresh()

	def OnIdle(self, event):
		event.GetId()
		tool = self.mtb.FindTool(self.ID_RepoMode)
		if not tool:
			return
		if self._repoModeLocal != Deca.world.HgRepository.Local:
			self._repoModeLocal = Deca.world.HgRepository.Local
			if self._repoModeLocal:
				tool.SetBitmap(self._localBmp)
				tool.SetDisabledBitmap(self._localBmpGr)
				tool.SetShortHelp(_('Local history'))
				tool.SetLongHelp(_('Switch to remote repository'))
			else:
				tool.SetBitmap(self._remoteBmp)
				tool.SetDisabledBitmap(self._remoteBmpGr)
				tool.SetShortHelp(_('Master repository'))
				tool.SetLongHelp(_('Switch to local repository'))
			# redraw repository
			wx.CallAfter(self.FillRepoView)
		# if location changed
		self.mtb.EnableTool(self.ID_RepoMode, Deca.world.HgRepository.IsOk)
		if Deca.world.HgRepository.IsOk and self._wasChanged != Deca.world.HgRepository.IsWdChanged:
			self._wasChanged = Deca.world.HgRepository.IsWdChanged
			self.mtb.EnableTool(self.ID_Commit, self._wasChanged)
		event.Skip()

	def vsplitOnIdle( self, event ):
		event.GetId()
		self.vsplit.SetSashPosition( 100 )
		self.vsplit.Unbind( wx.EVT_IDLE )
	
	def hsplitOnIdle( self, event ):
		event.GetId()
		self.hsplit.SetSashPosition( 180 )
		self.hsplit.Unbind( wx.EVT_IDLE )

	def OnTxtResize(self, evt):
		txtsz = self.txtDiff.GetSize()
		sz = self.txtwid
		if sz < txtsz[0]:
			sz = txtsz[0]
		self.txtDiff.SetColumnWidth(0, width=sz)
		evt.Skip()

	def OnCommit(self, event):
		event.GetId()
		if not Deca.world.HgRepository.IsWdChanged:
			return
		if Deca.world.HgRepository.User == '':
			dlg = UserPassDlg(self)
			dlg.Label = _("Code repository account:")
			if dlg.ShowModal() == wx.ID_OK:
				Deca.world.HgRepository.User = dlg.txtUname.GetValue()
				Deca.world.HgRepository.Password = dlg.txtPassword.GetValue()
				Profile_Set('HG_USER', Deca.world.HgRepository.User)
				Profile_Set('HG_PASSWD', Deca.world.HgRepository.Password)
				Deca.world.HgRepository.reopen()
		dlg = wx.TextEntryDialog(self, _("Describe revision:"),_('Commit'))
		dlg.SetValue("Auto-commit")
		if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
			try:
				Deca.world.HgRepository.commit(dlg.GetValue())
			except Exception as cond:
				wx.GetApp().log("[SourceControl] err: %s" % cond)
		# committed
		self.FillRepoView()

	def OnPush(self, event):
		event.GetId()
		HgCommon.HgPush(Deca.world.HgRepository, self)

	def OnPull(self, event):
		event.GetId()
		HgCommon.HgSync(Deca.world.HgRepository, self)

	def OnChangeLocation(self, event):
		if event is not None:
			event.GetId()
		tool = self.mtb.FindTool(self.ID_RepoMode)
		if not tool:
			return
		isLocal= not self._repoModeLocal
		if isLocal:
			Deca.world.HgRepository.SwitchToLocal()
		else:
			Deca.world.HgRepository.SwitchToRemote()
		# redraw repository and change button state will be performed in OnIdle

	def OnRevSelected(self, event):
		idx = self.repoHistory.GetFirstSelected()
		if idx == 0:
			# working copy
			files = Deca.world.HgRepository.status()
		elif idx == self.repoHistory.GetItemCount() - 1:
			# initial revision
			try:
				cr = int(self.repoHistory.GetItem(idx, col=1).GetText())
			except Exception:
				cr = self.repoHistory.GetItemCount() - idx - 1
			files = [('A', it[4]) for it in Deca.world.HgRepository.Repo.manifest(cr)]
		else:
			# ordinal revision
			try:
				cr = int(self.repoHistory.GetItem(idx, col=1).GetText())
			except Exception:
				cr = self.repoHistory.GetItemCount() - idx - 1
			try:
				pr = int(self.repoHistory.GetItem(idx+1, col=1).GetText())
			except Exception:
				pr = cr - 1
			files = Deca.world.HgRepository.status([pr,cr])
		self.fileList.DeleteAllItems()
		for fl in files:
			item = list(fl)
			pos = self.fileList.Append(item)
			if item[0] == u'A' :
				self.fileList.SetItemTextColour(pos, col=wx.ColorRGB(0x8080ff))
		event.Skip()

	def OnFileSelected(self, event):
		rev = self.repoHistory.GetFirstSelected()
		idx = self.fileList.GetFirstSelected()
		cod = self.fileList.GetItem(idx, col=0).GetText()
		fname = self.fileList.GetItem(idx, col=1).GetText()
		if rev == self.repoHistory.GetItemCount() - 1 or cod == '?':
			# initial revision
			lines = Deca.world.HgRepository.Repo.cat([os.path.join(Deca.world.HgRepository.Repo.root(), fname)])
			self.txtDiff.DeleteAllItems()
			#self.txtDiff.SetValue(lines)
			self.txtwid = 0
			f = self.txtDiff.GetFont()
			dc = wx.WindowDC(self.txtDiff)
			dc.SetFont(f)
			for l in lines.split('\n'):
				l = l.strip()
				self.txtDiff.Append([l])
				ext = dc.GetTextExtent(l)
				if ext[0] > self.txtwid:
					self.txtwid = ext[0]
			self.txtDiff.SetColumnWidth(0, width=self.txtwid + 20)
		else:
			try:
				cr = int(self.repoHistory.GetItem(rev, col=1).GetText())
			except Exception:
				cr = self.repoHistory.GetItemCount() - rev - 1
			try:
				pr = int(self.repoHistory.GetItem(rev+1, col=1).GetText())
			except Exception:
				pr = cr - 1

			if rev == 0:
				# working copy
				lines = Deca.world.HgRepository.Repo.diff(files=[os.path.join(Deca.world.HgRepository.Repo.root(), fname)],
								ignorespacechange=True, ignoreblanklines=False)
			else:
				lines = Deca.world.HgRepository.Repo.diff(files=[os.path.join(Deca.world.HgRepository.Repo.root(), fname)],
								revs=[pr,cr], ignorespacechange=True, ignoreblanklines=False)
			self.txtDiff.DeleteAllItems()
			lines = lines.split('\n')
			self.txtwid = 0
			f = self.txtDiff.GetFont()
			dc = wx.WindowDC(self.txtDiff)
			dc.SetFont(f)
			for l in lines[3:]:
				if len(l) > 1:
					ll = l[0]
					l = l.strip()
					if ll.isspace():
						l = ll + l
				itm = self.txtDiff.Append([l])
				ext = dc.GetTextExtent(l)
				if ext[0] > self.txtwid:
					self.txtwid = ext[0]
				if l.startswith('@@'):
					self.txtDiff.SetItemBackgroundColour(itm, col=self.colors[self.color_scheme][0])
					self.txtDiff.SetItemTextColour(itm, col=self.colors[self.color_scheme][1])
				elif l.startswith('+'):
					self.txtDiff.SetItemTextColour(itm, col=self.colors[self.color_scheme][2])
				elif l.startswith('-'):
					self.txtDiff.SetItemTextColour(itm, col=self.colors[self.color_scheme][3])
			self.txtDiff.SetColumnWidth(0, width=self.txtwid + 20)
		self.OnTxtResize(event)
		event.Skip()

	#noinspection PyTypeChecker
	def FillRepoView(self):
		if Deca.world.HgRepository.IsOk:
			self.repoHistory.DeleteAllItems()
			revlst = Deca.world.HgRepository.colored(include_wd = True)
			dt = datetime.now()
			for rev in revlst:
				tout = _('now')
				if isinstance(rev[6], datetime):
					diff = dt - rev[6]
					td = diff.seconds
					if td < 3 :
						tout = _('now')
					elif td < 60:
						tout = _('%d sec') % td
					else:
						td /= 60
						if td < 90:
							tout = _('%d min') % td
						else:
							td /= 60
							if td < 48:
								tout = _('%d hours') % td
							else:
								td /= 24
								if td < 45:
									tout = _('%d days') % td
								elif td < 365:
									tout = _('%d months') % (td / 30)
								else:
									tout = _('%d years') % (td / 365)
							# days
						# minutes
					# not a seconds
				# if a real date
				item = ['', rev[0], rev[3], rev[5], rev[4], tout, rev[2]]
				self.repoHistory.Append(item) # ii =
				# use ii to draw graph
		pass

	def OnRefresh(self, event):
		event.GetId()
		self.FillRepoView()
