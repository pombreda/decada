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
#!/usr/bin/python
import os
import sys
import wx
import wx.lib.agw.aui as aui
import wx.lib.ogl as ogl

from Editra.src.profiler import Profile_Get, Profile_Set
from Editra.src import ed_style
import Editra.src.ed_art as ed_art
import Editra.src.ed_glob as ed_glob
import Editra.src.util as util
import Editra.src.plugin as plugin
import Editra.src.profiler as profiler
import Editra.src.ed_i18n as ed_i18n
import HgCommon

from NbookPanel import PyShellView
import RepoView
from ShapeEditor import ShapeEdPanel
import ScEditor
import Explorer
import ScGraph
import Settings
import ObjRepo
import PropertySheet
import HtmlView
import ImgView
from AboutDlg import AboutBox

import Deca

import locale
import gettext
_ = gettext.gettext

__author__ = 'Stinger'
__revision__ = "$Revision: 0 $"

assertMode = wx.PYAPP_ASSERT_DIALOG

class Log:
	def __init__(self, frame = None) :
		self.Frame = frame

	def WriteText(self, text):
		if text.startswith("[ed_txt]") : return
		if text.startswith("[pycomp]") : return
		if text[-1:] == '\n':
			text = text[:-1]
		#wx.LogMessage(text)
		try:
			if self.Frame is not None:
				self.Frame.LogMessage(text)
		except Exception:
			pass

	write = WriteText
	__call__ = WriteText

	def flush(self):
		pass

class PyAUIFrame(wx.Frame):

	ID_CreateWorld = wx.NewId()
	ID_SaveWorld = wx.NewId()
	ID_OpenWorld = wx.NewId()
	ID_OpenWorldFile = wx.NewId()
	ID_OpenWorldReduced = wx.NewId()
	ID_OpenWorldMerge = wx.NewId()
	ID_Settings = wx.NewId()
	ID_About = wx.NewId()
	ID_ViewMenu = wx.NewId()
	ID_ViewExplorer = wx.NewId()
	ID_ViewProps = wx.NewId()
	ID_ViewLogger = wx.NewId()
	ID_ViewConsole = wx.NewId()
	ID_ItemMenu = wx.NewId()
	ID_ImageLib = wx.NewId()
	ID_HelpView = wx.NewId()

	ID_UserButton = wx.NewId()

	def __init__(self, parent, title="", pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
											wx.SUNKEN_BORDER |
											wx.CLIP_CHILDREN):

		self.log = Log(self)
		#self.log.write("Images will now be provided by SampoArt\n")
		wx.ArtProvider.PushProvider(ed_art.EditraArt())


		wx.Frame.__init__(self, parent, wx.ID_ANY, title, pos, size, style)

		self._perspectives = []
		self.n = 0
		self.x = 0

		util.SetWindowIcon(self)

		self.style = Profile_Get('SYNTHEME', 'str', 'default')
		self.statusbar = self.CreateStatusBar(3) #, wx.ST_SIZEGRIP
		self.statusbar.SetStatusWidths([-1, 24, 150])
		self.statusbar.SetStatusText(_("Welcome To Sampo Framework"), 0)
		self._status_icon = wx.StaticBitmap(self.statusbar, wx.ID_ANY, wx.Image(os.path.join("pixmaps","ledgray.png")).ConvertToBitmap())
		self._gauge = wx.Gauge(self.statusbar, wx.ID_ANY)
		self._gauge.SetRange(100)

		# tell FrameManager to manage this frame
		self._mgr = aui.AuiManager()
		self._mgr.SetManagedWindow(self)

		#   Open sub-menu
		self._open_menu = wx.Menu()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU, wx.Size(16, 16))
		mi = self._open_menu.AppendItem( wx.MenuItem( self._open_menu, self.ID_OpenWorldFile, _("&Open world")) )
		mi.SetBitmap(tbmp)
		self._open_menu.AppendItem( wx.MenuItem( self._open_menu, self.ID_OpenWorldMerge, _("Merge with another world")) )
		self._open_menu.AppendItem( wx.MenuItem( self._open_menu, self.ID_OpenWorldReduced, _("Open world without restoring views")) )
		# min size for the frame itself isn't completely done.
		# see the end up FrameManager::Update() for the test
		# code. For now, just hard code a frame minimum size
		self.SetMinSize(wx.Size(400, 300))

		# create some toolbars
		tb1 = aui.AuiToolBar(self, -1)
		tb1.SetToolBitmapSize(wx.Size(16,16))
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_NEW), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_CreateWorld, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("New world"), _("Create new empty world"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_OpenWorld, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Open world"), _("Open world from storage"), None)
		tb1.SetToolDropDown(self.ID_OpenWorld, True)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAVE), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_SaveWorld, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Save world"), _("Save world to storage"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_Settings, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Options"), _("Tune the framework"), None)
		tb1.AddSeparator()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_LAYER), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(Explorer.expPanel.ID_AddLayer, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add layer"), _("Create new empty layer"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_IMAGES), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_ImageLib, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Images"), _("Edit images library"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_ENGINE), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(Explorer.expPanel.ID_ERefresh, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Reload engines"), _("Rebuild engines tree and reinitialize packages"), None)
		tb1.AddSeparator()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_COMPUTER), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_ViewMenu, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("View"), _("Select visible components"), None)
		tb1.SetToolDropDown(self.ID_ViewMenu, True)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_HELP), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_HelpView, '', tbmp, tbmp, wx.ITEM_NORMAL, _("Help"), _("Show the help browser"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ABOUT), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_About, '', tbmp, tbmp, wx.ITEM_NORMAL, _("About"), _("About the framework"), None)
		tb1.Realize()

		self.tb2 = None

		# add a bunch of panes
		self.propgrid = PropertySheet.PropGridPanel(self)
		self._mgr.AddPane(self.propgrid, aui.AuiPaneInfo().
						  Name("props").Caption("Properties").
						  Right().CloseButton(True).MaximizeButton(True))
		self.propgrid.SetPropObject(Deca.world)
		self.explorer = Explorer.expPanel(self, wx.Point(0, 0), wx.Size(160, 250))
		self.explorer.UpdateWorldTree()
		self._mgr.AddPane(self.explorer, aui.AuiPaneInfo().
						  Name("explorer").Caption("World").
						  Left().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))

		self.logger = wx.TextCtrl(self,-1, "", wx.Point(0, 0), wx.Size(150, 90),
						   wx.NO_BORDER | wx.TE_MULTILINE)
		self._mgr.AddPane(self.logger, aui.AuiPaneInfo().
						  Name("logger").Caption("Logs & Messages").
						  Bottom().Layer(1).Position(1).CloseButton(True).MaximizeButton(True))

		# create some center panes
		self.nbook = aui.AuiNotebook(self)
		self.shell = PyShellView(self.nbook)
		if Profile_Get('ALLOW_CONSOLE', 'bool', True):
			self.AddTab(self.shell, self.shell.Title)
		self.UpdateIndexes()

		self._mgr.AddPane(self.nbook, aui.AuiPaneInfo().Name("notebook").
						  CenterPane())

		# add the toolbars to the manager

		self._mgr.AddPane(tb1, aui.AuiPaneInfo().
						  Name("tb1").Caption("MainToolbar").
						  ToolbarPane().Top().Row(0).Position(0).
						  LeftDockable(False).RightDockable(False))

		# make some default perspectives

		perspective_all = self._mgr.SavePerspective()

		all_panes = self._mgr.GetAllPanes()

		for ii in xrange(len(all_panes)):
			all_panes[ii].MinimizeMode(aui.AUI_MINIMIZE_CAPT_SMART | (all_panes[ii].GetMinimizeMode() & aui.AUI_MINIMIZE_POS_MASK))
			if not all_panes[ii].IsToolbar():
				all_panes[ii].Hide()

		self._mgr.GetPane("props").Show()
		self._mgr.GetPane("explorer").Show().Left().Layer(0).Row(0).Position(0)
		self._mgr.GetPane("logger").Show().Bottom().Layer(0).Row(0).Position(0)
		self._mgr.GetPane("notebook").Show()

		perspective_default = self._mgr.SavePerspective()

		self._perspectives.append(perspective_default)
		self._perspectives.append(perspective_all)

		# "commit" all changes made to FrameManager
		self._mgr.Update()

		#self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
		self.sizeChanged = False
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)

		# Show How To Use The Closing Panes Event
		self.Bind(aui.EVT_AUI_PANE_CLOSE, self.OnPaneClose)

		self.Bind(wx.EVT_MENU, self.OnNewWorld, id=self.ID_CreateWorld)
		self.Bind(wx.EVT_MENU, self.DoOpenWorld, id=self.ID_OpenWorldFile)
		self.Bind(wx.EVT_MENU, self.DoOpenWorld, id=self.ID_OpenWorldReduced)
		self.Bind(wx.EVT_MENU, self.DoOpenWorld, id=self.ID_OpenWorldMerge)
		self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnOpenWorld, id=self.ID_OpenWorld)
		self.Bind(wx.EVT_MENU, self.OnSaveWorld, id=self.ID_SaveWorld)

		self.Bind(wx.EVT_MENU, self.OnSettings, id=self.ID_Settings)
		self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
		self.Bind(wx.EVT_MENU, self.OnAbout, id=self.ID_About)
		self.Bind(wx.EVT_MENU, self.OnHelpView, id=self.ID_HelpView) 
		self.Bind(wx.EVT_MENU, self.OnImageLib, id=self.ID_ImageLib) 
		self.Bind(wx.EVT_MENU, self.OnNewLayer, id=Explorer.expPanel.ID_AddLayer)

		#self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewMenu)
		self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnPaneViewMenu, id=self.ID_ViewMenu)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewExplorer)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewProps)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewLogger)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewConsole)

		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=ed_glob.ID_SHOW_AUTOCOMP)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_FIND)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord(' '), ed_glob.ID_SHOW_AUTOCOMP ),
										 (wx.ACCEL_CTRL, ord('Q'), wx.ID_EXIT),
										 (wx.ACCEL_CTRL, ord('S'), wx.ID_SAVE),
										 (wx.ACCEL_CTRL, ord('O'), wx.ID_OPEN),
										 (wx.ACCEL_CTRL, ord('F'), wx.ID_FIND)
										])
		self.SetAcceleratorTable(accel_tbl)
		self.UpdateColors(self.style)
		wx.CallAfter(self._FixTbarsView)

	def AddTab(self, control, title="", img=None, active=False):
		""" Add control to the new page of the main notebook
		"""
		if img is None:
			img = control.GetTabImage()
		self.nbook.AddPage(control, caption=title, select=active, bitmap=img)
		self.UpdateIndexes()
		# fix event bindings
		for child in self.nbook.GetChildren():
			if isinstance(child, aui.AuiTabCtrl):
				child.Bind(wx.EVT_LEFT_DCLICK, self.OnTabCtrlLeftDClick)
		self.Update()

	def UpdateIndexes(self):
		"""Update all page indexes"""
		pages = [self.nbook.GetPage(page) for page in range(self.nbook.GetPageCount())]
		for idx, page in enumerate(pages):
			if page.Tag != "Console":
				page.SetTabIndex(idx)

	#noinspection PyBroadException
	def LogMessage(self, text):
		#skip mode
		try:
			self.logger.AppendText(text + "\n")
		except Exception:
			pass

	def OnSize(self, evt):
		evt.GetId()
		self.Reposition()  # for normal size events

		# Set a flag so the idle time handler will also do the repositioning.
		# It is done this way to get around a buglet where GetFieldRect is not
		# accurate during the EVT_SIZE resulting from a frame maximize.
		self.sizeChanged = True

	def OnIdle(self, evt):
		evt.GetId()
		if self.sizeChanged:
			self.Reposition()

	# reposition the checkbox
	def Reposition(self):
		rect = self.statusbar.GetFieldRect(1)
		self._status_icon.SetPosition((rect.x+2, rect.y+2))
		self._status_icon.SetSize((rect.width-4, rect.height-4))

		rect = self.statusbar.GetFieldRect(2)
		self._gauge.SetPosition((rect.x+2, rect.y+2))
		self._gauge.SetSize((rect.width-4, rect.height-4))
		self.sizeChanged = False

	def OnNewWorld(self, event):
		if Deca.world.Modified:
			resp = wx.MessageBox(_("Do you want to save current work?"), _("Sampo Framework"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
			if resp == wx.CANCEL:
				return
			if resp == wx.YES:
				self.OnSaveWorld(event)
		while self.nbook.GetPageCount() > 0:
			self.ClosePage(0)
		Deca.CreateWorld()
		profiler.TheProfile.Load(os.path.join(ed_glob.CONFIG['PROFILE_DIR'], "default.ppb"))
		profiler.TheProfile.Update()
		if Profile_Get('SHOW_CONSOLE', 'bool', True):
			self.shell.Show()
			self.AddTab(self.shell, self.shell.Title)
		wx.GetApp().ReloadTranslation()
		self.UpdateColors(Profile_Get('SYNTHEME', 'default'))
		self.explorer.UpdateWorldTree()
		self.SetTitle(_('[Untitled] - Sampo Framework'))

	def DoOpenWorld(self, event):
		evt_id = event.GetId()
		if evt_id == self.ID_OpenWorldFile or evt_id == self.ID_OpenWorldReduced:
			if Deca.world.Modified:
				resp = wx.MessageBox(_("Do you want to save current work?"), _("Sampo Framework"), wx.YES_NO|wx.CANCEL|wx.ICON_QUESTION)
				if resp == wx.CANCEL:
					return
				if resp == wx.YES:
					self.OnSaveWorld(event)
			# request filename
			dlg = wx.FileDialog(self, wildcard="DECA files|*.deca|All files|*.*", style=wx.FD_OPEN)
			if dlg.ShowModal() == wx.ID_OK :
				while self.nbook.GetPageCount() > 0:
					self.ClosePage(0)
				self.nbook.Update()
				Deca.CreateWorld(dlg.Path)
				profiler.TheProfile.Load(os.path.join(ed_glob.CONFIG['PROFILE_DIR'], "default.ppb"))
				wx.GetApp().ReloadTranslation()
				profiler.TheProfile.Update()
				if Deca.world.HgRepository.User == '':
					Deca.world.HgRepository.User = Profile_Get('HG_USER', 'str', '')
					Deca.world.HgRepository.Password = Profile_Get('HG_PASSWD', 'str', '')
					Deca.world.HgRepository.reopen()
				try:
					HgCommon.HgSync(Deca.world.HgRepository, None)
					Deca.world.HgRepository.SwitchToLocal()
					Deca.world.HgRepository.commit('Automatic sync to server on startup')
				except Exception as cond:
					self.LogMessage("[Source control][err] Synchronize failed: %s" % cond)
				finally:
					Deca.world.HgRepository.SwitchToLocal()


				if Profile_Get('SHOW_CONSOLE', 'bool', True):
					self.shell.Show()
					self.AddTab(self.shell, self.shell.Title)
				if evt_id == self.ID_OpenWorldFile:
					pg_list = Profile_Get('VIEW_PAGES', 'list', [])
					for pg in pg_list:
						tag = pg[0]
						#self.log("[DoOpenWorld][dbg] page = %s" % str(pg))
						if tag == "Text":
							fn = ''
							if pg[1][1] == ScEditor.EditorPanel.ED_TypeScript:
								fn = os.path.join(Deca.world.EnginesPath, pg[1][0])
							elif pg[1][1] == ScEditor.EditorPanel.ED_TypeReport:
								fn = os.path.join(Deca.world.ReportsPath, pg[1][0])
							if os.path.exists(fn):
								self.CreateTextWindow(fn, pg[1][1], activate=pg[2])
						elif tag == "Text Shape":
							fn = os.path.join(Deca.world.ShapesPath, pg[1])
							if os.path.exists(fn):
								px = ShapeEdPanel(self)
								px.tx.LoadFile(fn)
								ttl = px.tx.GetTitleString()
								self.AddTab(px, ttl, active=pg[2])
						elif tag == "Graph":
							px = ScGraph.GraphPanel(pg[1], self)
							self.AddTab(px, pg[1], active=pg[2])
						elif tag == "Repo":
							px = ObjRepo.RepositoryPanel(self)
							self.AddTab(px, px.Title, active=pg[2])
						elif tag == "RepoView":
							px = RepoView.RepoView(self)
							self.AddTab(px, px.Title, active=pg[2])
						elif tag == "HtmlView":
							px = HtmlView.HtmlPanel(self)
							self.AddTab(px, px.Title, active=pg[2])
						elif tag == "ImgView":
							px = ObjRepo.RepositoryPanel(self)
							self.AddTab(px, px.Title, active=pg[2])
					# for each saved page
				# if need to restore pages
				self.UpdateColors(Profile_Get('SYNTHEME', default='default'))
				self.explorer.UpdateWorldTree()
				# restore window position
				pdata = Profile_Get('WINDOW_STATE', default=False)
				self.Maximize(pdata)
				pdata = Profile_Get('WINDOW_POS') #, default=None
				if pdata:
					self.SetPosition(pdata)
				pdata = Profile_Get('WINDOW_SIZE') #, default=None
				if pdata:
					self.SetSize(pdata)
				pdata = Profile_Get('WINDOW_LAYOUT') #, default=None
				if pdata:
					self._mgr.LoadPerspective(pdata)
				Deca.world.HgRepository.User = Profile_Get('HG_USER', '')
				Deca.world.HgRepository.Password = Profile_Get('HG_PASSWD', '')
				Deca.world.HgRepository.AddRemove = Profile_Get('HG_AUTOFILES', '')
				self.SetTitle(_('[%s] - Sampo Framework') % os.path.basename(Deca.world.Filename))
			# if file selected
		elif evt_id == self.ID_OpenWorldMerge:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		else:
			event.Skip()

	def OnOpenWorld(self, event):
		if event.IsDropDownClicked():
			tb = event.GetEventObject()
			tb.SetToolSticky(event.GetId(), True)
			# line up our menu with the button
			rect = tb.GetToolRect(event.GetId())
			pt = tb.ClientToScreen(rect.GetBottomLeft())
			pt = self.ScreenToClient(pt)

			self.PopupMenu(self._open_menu, pos=pt)
			# make sure the button is "un-stuck"
			tb.SetToolSticky(event.GetId(), False)
		else:
			event.SetId(self.ID_OpenWorldFile)
			self.DoOpenWorld(event)

	def OnSaveWorld(self, event):
		event.GetId()
		fname = None
		if Deca.world.Initial:
			# request filename
			dlg = wx.FileDialog(self, wildcard="DECA files|*.deca|All files|*.*",
								style=wx.FD_SAVE)
			if dlg.ShowModal() == wx.ID_OK :
				fname = dlg.Path
				if os.path.splitext(fname)[1].lower() != '.deca' :
					fname += '.deca'
			else :
				return
		profiler.TheProfile.Write(Profile_Get('MYPROFILE'))
		# save window position
		Profile_Set('WINDOW_POS', self.GetPositionTuple())
		Profile_Set('WINDOW_SIZE', self.GetSizeTuple())
		Profile_Set('WINDOW_STATE', self.IsMaximized())
		Profile_Set('WINDOW_LAYOUT', self._mgr.SavePerspective())
		Profile_Set('HG_USER', Deca.world.HgRepository.User)
		Profile_Set('HG_PASSWD', Deca.world.HgRepository.Password)
		Profile_Set('HG_AUTOFILES', Deca.world.HgRepository.AddRemove)
		# save open tabs
		pg_list = []
		active_idx = self.nbook.GetSelection()
		for idx in range(self.nbook.GetPageCount()):
			pg = self.nbook.GetPage(idx)
			if pg.Tag != "Console":
				pg_list.append((pg.Tag, pg.GetParams(), idx == active_idx))
		Profile_Set('VIEW_PAGES', pg_list)
		Deca.world.Save(fname)
		self.SetTitle(_('[%s] - Sampo Framework') % os.path.basename(Deca.world.Filename))

	def OnPageClose(self, event):
		self.ClosePage(self.nbook.GetSelection())
		event.Veto()

	def ClosePage(self, idx):
		"""ClosePage(self, idx)

		Closes notebook page by index. May be used in user scripts.
		"""
		pg = self.nbook.GetPage(idx)
		if pg.Tag == 'Console' :
			self.nbook.RemovePage(idx)
			self.shell.Hide()
			Profile_Set('SHOW_CONSOLE', False)
		else:
			self.nbook.DeletePage(idx)

	def IsEditorMaximized(self):
		"""Is the editor pane maximized?
		return: bool
		"""
		bEditMax = True
		# If any other pane is open then the editor is not maximized
		for pane in self._mgr.GetAllPanes():
			if pane.IsShown() and pane.name != "notebook" and pane.name != "tb2" and pane.name != "tb1":
				bEditMax = False
				break
		return bEditMax

	def GetNotebook(self):
		return self.nbook.GetPage(self.nbook.GetSelection())

	def OnTabCtrlLeftDClick(self, event):
		x,y = event.GetPosition()
		for child in self.nbook.GetChildren():
			if isinstance(child, aui.AuiTabCtrl):
				if child.TabHitTest(x, y):
					# maximize pane
					paneInfo = self._mgr.GetPane("notebook")
					if self.IsEditorMaximized():
						self._mgr.RestorePane(paneInfo)
						#ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_RESTORE, context=self.GetId())
					else:
						self._mgr.MaximizePane(paneInfo)
					self._mgr.Update()
					return
		event.Skip()

	def OnPaneClose(self, event):
		#caption = event.GetPane().name
		event.Skip()
#        if caption in [u"logger", u"explorer", u"props"]:
#            event.GetPane().Hide()
#            event.Veto()

	def RestorePane(self, name):
		p = self._mgr.GetPane(name)
		if p is not None:
			p.Show()
			self._mgr.Update()

	def DispatchToControl(self, evt):
		chld = self.nbook.GetPage(self.nbook.GetSelection())
		#self.LogMessage("[dbg] dispatch event %i" % evt.GetId())
		if chld.Tag == "Text":
			chld.DispatchToControl(evt)
		if evt.GetId() == wx.ID_SAVE:
			self.OnSaveWorld(evt)
		if evt.GetId() == wx.ID_OPEN:
			evt.SetId(self.ID_OpenWorldFile)
			self.DoOpenWorld(evt)			
		pass

	def OnClose(self, event):
		profiler.TheProfile.Write(Profile_Get('MYPROFILE'))
		event.GetId()
		self._mgr.UnInit()
		del self._mgr
		self.Destroy()

	def OnExit(self, event):
		event.GetId()
		self.Close()

	def OnAbout(self, event):
		event.GetId()

		dlg = AboutBox(self)
		dlg.ShowModal()
		dlg.Destroy()

	def OnNewLayer(self, event):
		event.GetId()
		dlg = wx.TextEntryDialog(self, _("Enter new layer's name"), _('New Layer'))
		dlg.SetValue("Default")
		if dlg.ShowModal() == wx.ID_OK : 
			if dlg.GetValue() != '' and not dlg.GetValue().startswith('@'):
				Deca.world.GetLayer(dlg.GetValue())
			else :
				wx.MessageBox(_("Can't create layer with given name"), _('Sampo Framework'), wx.OK|wx.ICON_ERROR)
			self.explorer.UpdateWorldTree(Explorer.expPanel.updateTree_Layers)
		dlg.Destroy()
		pass

	def OnPaneViewMenu(self, event):
		if event.IsDropDownClicked():
			tb = event.GetEventObject()
			tb.SetToolSticky(event.GetId(), True)
			# create the popup menu
			cntxMenu = wx.Menu()
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ViewExplorer, _("View world &explorer"), wx.EmptyString, wx.ITEM_CHECK ) )
			if self._mgr.GetPane('explorer').IsShown() :
				it.Check(True)
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ViewProps, _("View &properties pane"), wx.EmptyString, wx.ITEM_CHECK ) )
			if self._mgr.GetPane('props').IsShown() :
				it.Check(True)
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ViewLogger, _("View &logs pane"), wx.EmptyString, wx.ITEM_CHECK ) )
			if self._mgr.GetPane('logger').IsShown() :
				it.Check(True)
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ViewConsole, _("View &console"), wx.EmptyString, wx.ITEM_CHECK ) )
			for idx in range(self.nbook.GetPageCount()):
				pg = self.nbook.GetPage(idx)
				if pg.Tag == 'Console' :
					it.Check(True)
			if not Profile_Get('ALLOW_CONSOLE', 'bool', True):
				it.Enable(False)
			# line up our menu with the button
			rect = tb.GetToolRect(event.GetId())
			pt = tb.ClientToScreen(rect.GetBottomLeft())
			pt = self.ScreenToClient(pt)

			self.PopupMenu(cntxMenu, pos=pt)
			# make sure the button is "un-stuck"
			tb.SetToolSticky(event.GetId(), False)
		pass

	def OnContextMenu(self, event):
		upd = False
		if event.GetId() == self.ID_ViewExplorer :
			upd = True
			p = self._mgr.GetPane('explorer')
			if p.IsShown() :
				self._mgr.ClosePane(p)
			else:
				p.Show()
		elif event.GetId() == self.ID_ViewProps :
			upd = True
			p = self._mgr.GetPane('props')
			if p.IsShown() :
				self._mgr.ClosePane(p)
			else:
				p.Show()
		elif event.GetId() == self.ID_ViewLogger :
			upd = True
			p = self._mgr.GetPane('logger')
			if p.IsShown() :
				self._mgr.ClosePane(p)
			else:
				p.Show()
		elif event.GetId() == self.ID_ViewConsole:
			present = False
			for idx in range(self.nbook.GetPageCount()):
				pg = self.nbook.GetPage(idx)
				if pg.Tag == 'Console' :
					self.ClosePage(idx)
					Profile_Set('SHOW_CONSOLE', False)
					present = True
					break
			self.nbook.Update()
			if not present and Profile_Get('ALLOW_CONSOLE', 'bool', True):
				self.shell.Show()
				self.AddTab(self.shell, self.shell.Title)
				Profile_Set('SHOW_CONSOLE', True)
		if upd :
			self._mgr.Update()

	def GetDockArt(self):
		return self._mgr.GetArtProvider()

	def DoUpdate(self):
		self._mgr.Update()

	def OnSettings(self, event):
		event.GetId()
		cursor = wx.BusyCursor()
		dlg = Settings.ScSettings(self)
		dlg.CenterOnParent()
		dlg.ShowModal()
		del cursor

	def GetStartPosition(self):
		self.x += 20
		x = self.x
		pt = self.ClientToScreen(wx.Point(0, 0))

		return wx.Point(pt.x + x, pt.y + x)

	def CreateTextWindow(self, fname, ftype=ScEditor.EditorPanel.ED_TypeScript, activate=False):
		if not os.path.exists(fname):
			fname = os.path.join(os.path.curdir, fname)
			open(fname, 'w').close()
		for i in range(self.nbook.GetPageCount()) :
			if self.nbook.GetPage(i).Tag == u"Text" and fname == self.nbook.GetPage(i).GetFileName():
				self.nbook.SetSelection(i)
				return

		pg = ScEditor.EditorPanel(ftype, self)
		pg.tx.LoadFile(fname)
		pg.tx.SaveFile(fname)
		ttl = pg.tx.GetTitleString()
		self.AddTab(pg, ttl, active=activate)
		sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.style))
		pg.UpdateColors(sm)

	def UpdateColors(self, style):
		#self.shell.SetShellTheme(style)
		self.style = style
		sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(style))
		for idx in xrange(self.nbook.GetPageCount()):
			self.nbook.GetPage(idx).UpdateColors(sm)
		# set logger window colors
		self.logger.SetBackgroundColour(sm.GetDefaultBackColour())
		self.logger.SetFont(sm.GetDefaultFont())
		self.logger.SetForegroundColour(sm.GetDefaultForeColour())
		self.logger.Refresh()
		# set explorer colors
		self.explorer.UpdateColors(sm)
		#self.explorer.SetHilightFocusColour()
		#self.explorer.SetHilightNonFocusColour()
		self.explorer.Refresh()
		# set properties colors
		self.propgrid.UpdateColors(sm)

	def SetStatus(self, text):
		"""SetStatus(self, text)

		:param text: text to be shown in the status bar
		"""
		self.SetStatusText(text, number=1)

	def SetStatusProgressRange(self, max_value):
		"""SetStatusProgressRange(self, max_value)

		:param max_value: the maximal limit of the progress range
		"""
		self._gauge.SetRange(max_value)

	def SetStatusProgress(self, percent):
		"""Set progress indicator in the status bar.
		:param percent: integer value in range [0..100] to indicate progress"""
		if type(percent) != int:
			percent = 0
		if percent < 0:
			percent = 0
		self._gauge.SetValue(percent)
		pass

	def OnHelpView(self, event):
		event.GetId()
		for i in range(self.nbook.GetPageCount()) :
			if self.nbook.GetPage(i).Tag == u"HtmlView":
				self.nbook.SetSelection(i)
				return
		pg = HtmlView.HtmlPanel(self)
		pg.UpdateColors(self.style)
		self.AddTab(pg, pg.Title, active=True)

	def OnImageLib(self, event):
		event.GetId()
		for i in range(self.nbook.GetPageCount()) :
			if self.nbook.GetPage(i).Tag == u"ImgView":
				self.nbook.SetSelection(i)
				return
		pg = ImgView.ImgPanel(self)
		sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.style))
		pg.UpdateColors(sm)
		self.AddTab(pg, pg.Title, active=True)

	def _InitUserToolbar(self):
		if self.tb2:
			pinfo = self._mgr.GetPane(self.tb2)
			self._mgr.ClosePane(pinfo)
			self._mgr.DetachPane(self.tb2)
			self.tb2.Destroy()
		self.tb2 = aui.AuiToolBar(self, -1)
		self.tb2.SetToolBitmapSize(wx.Size(16,16))
		self.tb2.AddSpacer(1)

	def _FixTbarsView(self):
		self._mgr.GetPaneByName("tb1").Gripper(False)
		self._mgr.GetPaneByName("tb2").Gripper(False)
		self._mgr.Update()

	def _CompleteUserToolbar(self):
		self.tb2.Realize()
		self._mgr.AddPane(self.tb2, aui.AuiPaneInfo().
						  Name("tb2").Caption("World Toolbar").
						  ToolbarPane().Top().Row(0).Position(1).
						  LeftDockable(False).RightDockable(False))
		self.tb2.Refresh()
		self._mgr.Update()
		wx.CallAfter(self._FixTbarsView)

	def AddUserTool(self, tool_id, img, short, long, handler):
		"""Add user defined tool button to the toolbar.
		@tool_id - unique 14-bit integer to identificate tool
		@img     - bitmap to draw on button
		@short   -
		@handler - event handler for the button
		"""
		if self.tb2.FindTool(tool_id) :
			self.log.write('[AddUserTool][warn] Tool ID=%s already exists' % tool_id)
			self.tb2.DeleteTool(tool_id)
		self.tb2.AddTool(tool_id, '', img, img, wx.ITEM_NORMAL,
						short, long, tool_id)
		self.Bind(wx.EVT_MENU, handler, id=tool_id)
		self.log.write('[AddUserTool][dbg] Tool ID=%s binded' % tool_id)

###########################################################################
## main Application class
###########################################################################
class RunApp(wx.App):
	def __init__(self, name):
		self.name = name
		self.useShell = True
		self.log = Log()
		self.curr_dir = os.path.dirname(sys.argv[0])
		if self.curr_dir == '':
			self.curr_dir = os.path.curdir
		self.curr_dir = os.path.abspath(self.curr_dir)
		sys.stderr = self.log
		sys.stdout = self.log
		imp_path = os.path.dirname(sys.modules['NbookPanel'].__file__)
		imp_path = os.path.join(imp_path, 'Editra')
		sys.path.append(imp_path)
		imp_path = os.path.join(imp_path, 'src')
		sys.path.append(imp_path)
		imp_path = os.path.join(imp_path, 'extern')
		sys.path.append(imp_path)
		wx.App.__init__(self, redirect=False)

	def OnInit(self):
		wx.Log_SetActiveTarget(wx.LogStderr())

		self.SetAssertMode(assertMode)

		# Resolve resource locations
		ed_glob.CONFIG['CONFIG_DIR'] = self.curr_dir
		ed_glob.CONFIG['INSTALL_DIR'] = self.curr_dir
		ed_glob.CONFIG['KEYPROF_DIR'] = os.path.join(self.curr_dir, u"ekeys")
		ed_glob.CONFIG['SYSPIX_DIR'] = os.path.join(self.curr_dir, u"pixmaps")
		ed_glob.CONFIG['PLUGIN_DIR'] = os.path.join(self.curr_dir, u"plugins")
		ed_glob.CONFIG['THEME_DIR'] = os.path.join(self.curr_dir, u"pixmaps", u"theme")
		ed_glob.CONFIG['LANG_DIR'] = os.path.join(self.curr_dir, u"locale")
		ed_glob.CONFIG['STYLES_DIR'] = os.path.join(self.curr_dir, u"styles")
		ed_glob.CONFIG['SYS_PLUGIN_DIR'] = os.path.join(self.curr_dir, u"plugins")
		ed_glob.CONFIG['SYS_STYLES_DIR'] = os.path.join(self.curr_dir, u"styles")
		ed_glob.CONFIG['TEST_DIR'] = os.path.join(self.curr_dir, u"tests", u"syntax")
		ed_glob.CONFIG['ISLOCAL'] = True
		ed_glob.CONFIG['PROFILE_DIR'] = os.path.join(self.curr_dir, u"profiles")
		ed_glob.CONFIG['GLOBAL_PROFILE_DIR'] = os.path.join(self.curr_dir, u"profiles")

		Deca.CreateWorld()

		profiler.TheProfile.Load(os.path.join(ed_glob.CONFIG['PROFILE_DIR'], "default.ppb"))
		profiler.TheProfile.Update()

		self._pluginmgr = plugin.PluginManager()

		self.ReloadTranslation()

		ogl.OGLInitialize()
		frame = PyAUIFrame(None, _("Sampo Framework"), size=(750, 570))
		frame.Show(True)

		self.SetTopWindow(frame)
		self.frame = frame
		self.log.Frame = frame

		return True

	def OnExit(self):
		Deca.world.Destroy()

	def GetLog(self):
		"""Returns the logging function used by the app
		@return: the logging function of this program instance
		"""
		return self.log

	def GetPluginManager(self):
		"""Returns the plugin manager used by this application
		@return: Apps plugin manager
		@see: L{plugin}
		"""
		return self._pluginmgr

	def ReloadArtProvider(self):
		"""Reloads the custom art provider onto the artprovider stack
		@postcondition: artprovider is removed and reloaded
		"""
		try:
			wx.ArtProvider.PopProvider()
		finally:
			wx.ArtProvider.PushProvider(ed_art.EditraArt())

	def ReloadTranslation(self):
		locale.setlocale(locale.LC_ALL, '')
		self.locale = wx.Locale(ed_i18n.GetLangId(profiler.Profile_Get('LANG')))
		if self.locale.GetCanonicalName() in ed_i18n.GetAvailLocales():
			self.locale.AddCatalogLookupPathPrefix(ed_glob.CONFIG['LANG_DIR'])
			self.locale.AddCatalog('sampo')
		else:
			del self.locale
			self.locale = None

	def RunEngine(self, fname):
		"""RunEngine(self, fname)

		Executes given engine from the world's storage.
		:param fname: path to engine's file relative to the world's engine storage
		"""
		base = os.path.join(Deca.world.EnginesPath, fname)
		fl = None
		try:
			fl = open(base, 'r')
			exec fl in globals()
		except Exception as cond:
			wx.MessageBox(_("Error execution %s!\n%s") % (fname, cond), _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			self.log("[exec][err] %s" % cond)
		finally:
			if fl : fl.close()
		return # no need to rebuild tree

if __name__ == '__main__':
	app = RunApp("Sampo")
	app.MainLoop()
