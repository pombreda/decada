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
import imp
import wx.lib.agw.aui as aui
import wx.lib.ogl as ogl
import shutil

from Editra.src.profiler import Profile_Get, Profile_Set
from Editra.src import ed_style
import Editra.src.ed_art as ed_art
import Editra.src.ed_glob as ed_glob
import Editra.src.util as util
import Editra.src.plugin as plugin
import Editra.src.profiler as profiler
import Editra.src.syntax.synglob as synglob
import Editra.src.ed_i18n as ed_i18n

from NbookPanel import PyShellView
from ShapeEditor import ShapeEdPanel
import ScEditor
import ScGraph
import Settings
import ObjRepo
import PyShell
import PropertySheet
import HtmlView
import ImgView
from Deca.Utility import ImportPackage, GetModule
from AboutDlg import AboutBox
from Reporter import ReportGenerator

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
		except:
			pass

	write = WriteText
	__call__ = WriteText

	def flush(self):
		pass

def engine_image(d, f):
	if os.path.isdir(os.path.join(d, f)):
		if os.path.exists(os.path.join(os.path.join(d, f), '__init__.py')):
			# import package
			pkf = os.path.join(d, f)
			pkn = pkf.replace(Deca.world.EnginesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			app.log("[engines][dbg] Add package %s (%s)" % (pkn, pkf))
			try:
				ImportPackage(pkn, pkf)
			except ImportError as cond:
				log = wx.GetApp().GetLog()
				log("[Engine rescan][err] %s" % cond)
			return 2 # imagelist.PACKAGE
		return 3 # imagelist.FOLDER
	ext = os.path.splitext(f)[1].lower()
	if ext == '.py':
		return 4 # imagelist.PYTHON
	if ext == '.pyc':
		return 5 # imagelist.PYTHON_BIN
	return 99 # imagelist.BAD_IMAGE

def engine_file(d, f):
	if os.path.isdir(os.path.join(d, f)):
		return True
	ext = os.path.splitext(f)[1].lower()
	if ext == '.py':
		return True
	if ext == '.pyc':
		return True
	return False

def engine_src(f, d):
	n, e = os.path.splitext(f)
	e = e[1:].lower()
	t = n + '.py'
	if e == 'pyc' and t in d.keys():
		return False
	return True

def engine_visit(arg, dname, flist):
	#find parent on current dirname
	parent = arg[1][dname]
	# transform flist into dict fname -> image, remove uninteresting entries
	folder = { f:engine_image(dname, f) for f in flist if engine_file(dname, f) }
	# remove binaries if source exists
	folder = { f:i for f,i in folder.items() if engine_src(f, folder)}
	# add items
	rp = parent
	for f,i in folder.items() :
		itm = rp = arg[0].InsertItem(parent, rp, os.path.splitext(f)[0], i)
		if i == 2 or i == 3:
			arg[1][os.path.join(dname, f)] = itm
			arg[0].SetPyData(itm, "EngineDir:%s" % os.path.join(dname, f))
		else:
			arg[0].SetPyData(itm, "EngineCod:%s" % os.path.join(dname, f))
	# all done

def report_image(d, f):
	if os.path.isdir(os.path.join(d, f)):
		return 3 # imagelist.FOLDER
	ext = os.path.splitext(f)[1].lower()
	if ext == '.xml':
		return 6 # imagelist.REPORT
	return 99 # imagelist.BAD_IMAGE

def reports_visit(arg, dname, flist):
	#find parent on current dirname
	parent = arg[1][dname]
	# transform flist into dict fname -> image, remove uninteresting entries
	folder = { f:report_image(dname, f) for f in flist if os.path.splitext(f)[1].lower() == '.xml' or os.path.isdir(os.path.join(dname, f)) }
	# add items
	rp = parent
	for f,i in folder.items() :
		itm = rp = arg[0].InsertItem(parent, rp, os.path.splitext(f)[0], i)
		if i == 3:
			arg[1][os.path.join(dname, f)] = itm
			arg[0].SetPyData(itm, "ReportDir:%s" % os.path.join(dname, f))
		else:
			arg[0].SetPyData(itm, "ReportCod:%s" % os.path.join(dname, f))
	# all done

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
	ID_AddLayer = wx.NewId()
	ID_RemoveLayer = wx.NewId()
	ID_ImageLib = wx.NewId()
	ID_AddEFolder = wx.NewId()
	ID_AddEPackage = wx.NewId()
	ID_AddECode = wx.NewId()
	ID_ReloadEPackage = wx.NewId()
	ID_ERemove = wx.NewId()
	ID_ERefresh = wx.NewId()
	ID_OpenECode = wx.NewId()
	ID_RunECode = wx.NewId()
	ID_ImportECode = wx.NewId()
	ID_AddRFolder = wx.NewId()
	ID_AddRCode = wx.NewId()
	ID_RRemove = wx.NewId()
	ID_RGenerate = wx.NewId()
	ID_RefreshWorld = wx.NewId()
	ID_RefreshLayers = wx.NewId()
	ID_RefreshEngines = wx.NewId()
	ID_RefreshReports = wx.NewId()
	ID_HelpView = wx.NewId()

	ID_UserButton = wx.NewId()

	updateTree_All 		= 0xFFFF
	updateTree_Layers 	= 0x0001
	updateTree_Engines 	= 0x0002
	updateTree_Reports 	= 0x0004

	def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
											wx.SUNKEN_BORDER |
											wx.CLIP_CHILDREN):

		self.log = Log(self)
		#self.log.write("Images will now be provided by SampoArt\n")
		wx.ArtProvider.PushProvider(ed_art.EditraArt())


		wx.Frame.__init__(self, parent, id, title, pos, size, style)

		# tell FrameManager to manage this frame
		self._mgr = aui.AuiManager()
		self._mgr.SetManagedWindow(self)

		self._perspectives = []
		self.n = 0
		self.x = 0

		util.SetWindowIcon(self)

		self.style = Profile_Get('SYNTHEME', 'str', 'default')
		self.statusbar = self.CreateStatusBar(2) #, wx.ST_SIZEGRIP
		self.statusbar.SetStatusWidths([-2, -3])
		self.statusbar.SetStatusText("Ready", 0)
		self.statusbar.SetStatusText("Welcome To SamPy Framework", 1)

		# min size for the frame itself isn't completely done.
		# see the end up FrameManager::Update() for the test
		# code. For now, just hard code a frame minimum size
		self.SetMinSize(wx.Size(400, 300))

		# create some toolbars
		tb1 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, aui.AUI_TB_HORZ_LAYOUT | aui.AUI_TB_GRIPPER)
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
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_LAYER), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_AddLayer, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add layer"), _("Create new empty layer"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_IMAGES), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_ImageLib, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Images"), _("Edit images library"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_ENGINE), wx.ART_MENU, wx.Size(16, 16))
		tb1.AddTool(self.ID_ERefresh, '', tbmp, tbmp, wx.ITEM_NORMAL,
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
		self.explorer = wx.TreeCtrl(self, -1, wx.Point(0, 0), wx.Size(160, 250),
						   wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
		self.UpdateWorldTree()
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
		#self.CreateGraphWindow("Graph")
		#pg = ObjRepo.RepositoryPanel(self)
		#self.AddTab(pg, pg.Title)
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
		#self.Bind(wx.EVT_SIZE, self.OnSize)
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
		self.Bind(wx.EVT_MENU, self.OnNewLayer, id=self.ID_AddLayer)

		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_AddEFolder)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_AddEPackage)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_AddECode)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_ERemove)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_OpenECode)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_RunECode)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_ReloadEPackage)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_ImportECode)
		self.Bind(wx.EVT_MENU, self.OnEngineMenu, id=self.ID_ERefresh)

		self.Bind(wx.EVT_MENU, self.OnReportMenu, id=self.ID_AddRFolder)
		self.Bind(wx.EVT_MENU, self.OnReportMenu, id=self.ID_AddRCode)
		self.Bind(wx.EVT_MENU, self.OnReportMenu, id=self.ID_RRemove)
		self.Bind(wx.EVT_MENU, self.OnReportMenu, id=self.ID_RGenerate)

		self.Bind(wx.EVT_MENU, self.OnLayerMenu, id=self.ID_RemoveLayer)

		self.Bind(wx.EVT_MENU, self.OnRefreshWorld, id=self.ID_RefreshWorld)
		self.Bind(wx.EVT_MENU, self.OnRefreshWorld, id=self.ID_RefreshLayers)
		self.Bind(wx.EVT_MENU, self.OnRefreshWorld, id=self.ID_RefreshEngines)
		self.Bind(wx.EVT_MENU, self.OnRefreshWorld, id=self.ID_RefreshReports)

		#self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewMenu)
		self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnPaneViewMenu, id=self.ID_ViewMenu)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewExplorer)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewProps)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewLogger)
		self.Bind(wx.EVT_MENU, self.OnContextMenu, id=self.ID_ViewConsole)
		self.Bind(wx.EVT_TREE_ITEM_MENU, self.OnViewMenu)
		self.explorer.Bind( wx.EVT_LEFT_DCLICK, self.OnExplDouble )
		self.explorer.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnExplChaged )

		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=ed_glob.ID_SHOW_AUTOCOMP)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.DispatchToControl, id=wx.ID_FIND)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord(' '), ed_glob.ID_SHOW_AUTOCOMP ),
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
		except:
			pass

	def ClosePage(self, idx):
		pg = self.nbook.GetPage(idx)
		if pg.Tag == 'Console' :
			self.nbook.RemovePage(idx)
			self.shell.Hide()
			Profile_Set('SHOW_CONSOLE', False)
		else:
			self.nbook.DeletePage(idx)

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
		wx.GetApp().self.ReloadTranslation()
		self.UpdateColors(Profile_Get('SYNTHEME', 'default'))
		self.UpdateWorldTree()

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

				if Profile_Get('SHOW_CONSOLE', 'bool', True):
					self.shell.Show()
					self.AddTab(self.shell, self.shell.Title)
				if evt_id == self.ID_OpenWorldFile:
					pg_list = Profile_Get('VIEW_PAGES', 'list', [])
					for pg in pg_list:
						tag = pg[0]
						#self.log("[DoOpenWorld][dbg] page = %s" % str(pg))
						if tag == "Text":
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
						elif tag == "HtmlView":
							px = HtmlView.HtmlPanel(self)
							self.AddTab(px, px.Title, active=pg[2])
						elif tag == "ImgView":
							px = ObjRepo.RepositoryPanel(self)
							self.AddTab(px, px.Title, active=pg[2])
					# for each saved page
				# if need to restore pages
				self.UpdateColors(Profile_Get('SYNTHEME', default='default'))
				self.UpdateWorldTree()
				# restore window position
				pdata = Profile_Get('WINDOW_STATE', default=False)
				self.Maximize(pdata)
				pdata = Profile_Get('WINDOW_POS', default=None)
				if pdata:
					self.SetPosition(pdata)
				pdata = Profile_Get('WINDOW_SIZE', default=None)
				if pdata:
					self.SetSize(pdata)
				pdata = Profile_Get('WINDOW_LAYOUT', default=None)
				if pdata:
					self._mgr.LoadPerspective(pdata)
			# if file selected
		elif evt_id == self.ID_OpenWorldMerge:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		else:
			event.Skip()

	def OnOpenWorld(self, event):
		if event.IsDropDownClicked():
			tb = event.GetEventObject()
			tb.SetToolSticky(event.GetId(), True)
			# create the popup menu
			cntxMenu = wx.Menu()
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_OpenWorldFile, _("&Open world")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_OpenWorldMerge, _("Merge with another world")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_OpenWorldReduced, _("Open world without restoring views")) )
			# line up our menu with the button
			rect = tb.GetToolRect(event.GetId())
			pt = tb.ClientToScreen(rect.GetBottomLeft())
			pt = self.ScreenToClient(pt)

			self.PopupMenu(cntxMenu, pt)
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
			else :
				return
		profiler.TheProfile.Write(Profile_Get('MYPROFILE'))
		# save window position
		Profile_Set('WINDOW_POS', self.GetPositionTuple())
		Profile_Set('WINDOW_SIZE', self.GetSizeTuple())
		Profile_Set('WINDOW_STATE', self.IsMaximized())
		Profile_Set('WINDOW_LAYOUT', self._mgr.SavePerspective())
		# save open tabs
		pg_list = []
		active_idx = self.nbook.GetSelection()
		for idx in range(self.nbook.GetPageCount()):
			pg = self.nbook.GetPage(idx)
			if pg.Tag != "Console":
				pg_list.append((pg.Tag, pg.GetParams(), idx == active_idx))
		Profile_Set('VIEW_PAGES', pg_list)
		Deca.world.Save(fname)

	def OnPageClose(self, event):
		if self.nbook.GetPage(self.nbook.GetSelection()).Tag == "Console":
			self.nbook.RemovePage(self.nbook.GetSelection())
			self.shell.Hide()
			event.Veto()

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
		event.GetId()
		pass
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
			self.OnOpenWorld(evt)			
		pass

	def OnClose(self, event):
		profiler.TheProfile.Write(Profile_Get('MYPROFILE'))
		event.GetId()
		self._mgr.UnInit()
		del self._mgr
		self.Destroy()

	def OnViewMenu(self, event):
		event.GetId()
		i = event.EventObject.Selection
		if i.IsOk() :
			ttl = event.EventObject.GetItemPyData(i)
			if ttl == 'World':
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddLayer, _("Add new layer"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendSeparator()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RefreshWorld, _("Refresh all"), wx.EmptyString, wx.ITEM_NORMAL ))
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RefreshLayers, _("Refresh layers"), wx.EmptyString, wx.ITEM_NORMAL ))
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RefreshEngines, _("Refresh engines"), wx.EmptyString, wx.ITEM_NORMAL ))
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RefreshReports, _("Refresh reports"), wx.EmptyString, wx.ITEM_NORMAL ))
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
			elif ttl[0:9] == 'EngineDir':
				pth = ttl[10:]
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddEFolder, _("Add new folder"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddEPackage, _("Add new package"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddECode, _("Add new code"), wx.EmptyString, wx.ITEM_NORMAL ) )
				if os.path.exists(os.path.join(pth, '__init__.py')):
					cntxMenu.AppendSeparator()
					cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ReloadEPackage, _("Reload package"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendSeparator()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ERemove, _("Remove"), wx.EmptyString, wx.ITEM_NORMAL ))
				if pth == Deca.world.EnginesPath:
					cntxMenu.Enable(self.ID_ERemove, enable=False)
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
			elif ttl[0:9] == 'EngineCod':
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_OpenECode, _("Open"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RunECode, _("Run code"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ImportECode, _("Import as module"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendSeparator()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_ERemove, _("Remove"), wx.EmptyString, wx.ITEM_NORMAL ))
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
			elif ttl[0:9] == 'ReportDir':
				pth = ttl[10:]
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddRFolder, _("Add new folder"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_AddRCode, _("Add new report"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendSeparator()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RRemove, _("Remove"), wx.EmptyString, wx.ITEM_NORMAL ))
				if pth == Deca.world.ReportsPath:
					cntxMenu.Enable(self.ID_RRemove, enable=False)
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
				pass
			elif ttl[0:9] == 'ReportCod':
				pth = ttl[10:]
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RGenerate, _("Generate"), wx.EmptyString, wx.ITEM_NORMAL ) )
				cntxMenu.AppendSeparator()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RRemove, _("Remove"), wx.EmptyString, wx.ITEM_NORMAL ))
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
				pass
			elif ttl == 'Repo':
				pass # nothing to do for repository
			elif ttl == 'layer':
				cntxMenu = wx.Menu()
				cntxMenu.AppendItem( wx.MenuItem( cntxMenu, self.ID_RemoveLayer, _("Remove"), wx.EmptyString, wx.ITEM_NORMAL ))
				pt = event.GetPoint()
				pt.x += event.EventObject.Position.x
				pt.y += event.EventObject.Position.y
				self.PopupMenu( cntxMenu, pos=pt )
			else:
				wx.MessageBox(event.EventObject.GetItemText(i), ttl, wx.OK)
		pass

	def OnRefreshWorld(self, event):
		if event.GetId() == self.ID_RefreshLayers:
			self.UpdateWorldTree(self.updateTree_Layers)
		elif event.GetId() == self.ID_RefreshEngines:
			self.UpdateWorldTree(self.updateTree_Engines)
		elif event.GetId() == self.ID_RefreshReports:
			self.UpdateWorldTree(self.updateTree_Reports)
		else:
			self.UpdateWorldTree(self.updateTree_All)

	def OnExplDouble(self, event):
		event.GetId()
		itm = self.explorer.GetSelection()
		msg = event.EventObject.GetItemText(itm)
		ttl = str(event.EventObject.GetItemPyData(itm))
		if itm.IsOk() :
			if ttl == u'Repo':
				for i in range(self.nbook.GetPageCount()) :
					if self.nbook.GetPage(i).Tag == u"Repo":
						self.nbook.SetSelection(i)
						self.nbook.GetPage(i).UpdateView(None)
						return
				pg = ObjRepo.RepositoryPanel(self)
				self.AddTab(pg, pg.Title, active=True)
				sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.style))
				pg.UpdateColors(sm)
			elif ttl == u'layer':
				for i in range(self.nbook.GetPageCount()) :
					pt = self.nbook.GetPageText(i)
					if self.nbook.GetPage(i).Tag == 'Graph' and self.nbook.GetPageText(i) == msg:
						self.nbook.SetSelection(i)
						return
				pg = ScGraph.GraphPanel(msg, self)
				self.AddTab(pg, msg, active=True)
				sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.style))
				pg.UpdateColors(sm)
			elif ttl.startswith('EngineCod') :
				self.CreateTextWindow(ttl[10:], activate=True)
			elif ttl.startswith('ReportCod') :
				self.CreateTextWindow(ttl[10:], ScEditor.EditorPanel.ED_TypeReport, activate=True)
		# valid item wx.MessageBox(msg, ttl, wx.OK)

	def OnExplChaged(self, event):
		event.GetId()
		itm = self.explorer.GetSelection()
		msg = event.EventObject.GetItemText(itm)
		ttl = str(event.EventObject.GetItemPyData(itm))
		if ttl == 'World' :
			self.propgrid.SetPropObject(Deca.world)
		elif ttl == 'Repo':
			obj = Deca.world.GetLayer(Deca.World.ID_Repository)
			self.propgrid.SetPropObject(obj)
		elif ttl == 'layer':
			obj = Deca.world.GetLayer(msg)
			self.propgrid.SetPropObject(obj)

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
			self.UpdateWorldTree(self.updateTree_Layers)
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

			self.PopupMenu(cntxMenu, pt)
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

	def UpdateWorldTree(self, mode = updateTree_All):
		if mode == self.updateTree_All:
			self.explorer.DeleteAllItems()
			root = self.explorer.AddRoot("World", image=0)
			self.explorer.SetPyData(root, obj='World')
			self._InitUserToolbar()
		else:
			root = self.explorer.GetRootItem()
			if mode & self.updateTree_Layers:
				it = self.explorer.GetFirstChild(root)[0]
				while it.IsOk():
					dl = it
					it = self.explorer.GetNextSibling(dl)
					if self.explorer.GetPyData(dl) == 'layer' :
						self.explorer.Delete(dl)
					# end if
				# end while
			if mode & self.updateTree_Engines:
				it = self.explorer.GetFirstChild(root)[0]
				while it.IsOk():
					dl = it
					it = self.explorer.GetNextSibling(dl)
					if self.explorer.GetPyData(dl).startswith('Engine') :
						self.explorer.Delete(dl)
					# end if
				# end while
				self._InitUserToolbar()
			if mode & self.updateTree_Reports:
				it = self.explorer.GetFirstChild(root)[0]
				while it.IsOk():
					dl = it
					it = self.explorer.GetNextSibling(dl)
					if self.explorer.GetPyData(dl).startswith('Report') :
						self.explorer.Delete(dl)
					# end if
				# end while

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_WORLD), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_LAYER), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_OBJECT), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_FOLDER), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(synglob.ID_LANG_PYTHON), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(synglob.ID_LANG_XML), wx.ART_MENU, wx.Size(16,16)))
		self.explorer.AssignImageList(imglist)

		if mode == self.updateTree_All:
			rp = self.explorer.InsertItemBefore(root, index=0, text=_("Repository"), image=2)
			self.explorer.SetPyData(rp, obj='Repo')
		else :
			rp = self.explorer.GetFirstChild(root)[0]
		# repository added
		if mode & self.updateTree_Layers :
			for ln in Deca.world.GetLayerList():
				if not ln.startswith('@') :
					rp = self.explorer.InsertItem(root, idPrevious=rp, text=ln, image=1)
					self.explorer.SetPyData(rp, obj='layer')
			# end layers iteration
		else :
			it = self.explorer.GetNextSibling(rp)
			while it.IsOk() and self.explorer.GetPyData(it) == 'layer':
				rp = it
				it = self.explorer.GetNextSibling(rp)
		# layer added

		if mode & self.updateTree_Engines :
			pth = Deca.world.EnginesPath
			rp = self.explorer.InsertItem(root, idPrevious=rp, text=_("Engines"), image=3)
			self.explorer.SetPyData(rp, obj='EngineDir:%s' % pth)
			try:
				os.path.walk(pth, engine_visit, [self.explorer, {pth:rp}])
			except Exception as cond:
				self.log("[engines walking][err] %s" % cond)
			self._CompleteUserToolbar()
		else :
			rp = self.explorer.GetNextSibling(rp)
		# engines added
		if mode & self.updateTree_Reports :
			pth = Deca.world.ReportsPath
			rp = self.explorer.InsertItem(root, idPrevious=rp, text=_("Reports"), image=3)
			self.explorer.SetPyData(rp, obj='ReportDir:%s' % pth)
			# todo: add Attachments and Results folders
			try:
				os.path.walk(pth, reports_visit, [self.explorer, {pth:rp}])
			except Exception as cond:
				self.log("[reports walking][err] %s" % cond)
		# reports added
		self.explorer.Expand(root)

	def CreateTextWindow(self, fname, ftype=ScEditor.EditorPanel.ED_TypeScript, activate=False):
		if not os.path.exists(fname):
			fname = os.path.join(os.path.curdir, fname)
			open(fname, 'w').close()
		for i in range(self.nbook.GetPageCount()) :
			if self.nbook.GetPage(i).Tag == u"Text" and fname == self.nbook.GetPage(i).GetFileName():
				self.nbook.SetSelection(i)
				return

		pg = ScEditor.EditorPanel(ftype, self)
		pg.tx.UpdateAllStyles(self.style)
		pg.tx.LoadFile(fname)
		ttl = pg.tx.GetTitleString()
		self.AddTab(pg, ttl, active=activate)

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
		self.explorer.SetBackgroundColour(sm.GetDefaultBackColour())
		self.explorer.SetForegroundColour(sm.GetDefaultForeColour())
		#self.explorer.SetHilightFocusColour()
		#self.explorer.SetHilightNonFocusColour()
		self.explorer.Refresh()
		# set properties colors
		self.propgrid.UpdateColors(sm)

	def OnEngineMenu(self, event):
		base = ''
		if event.GetId() != self.ID_ERefresh:
			base = self.explorer.GetPyData(self.explorer.GetSelection())
			base = base[10:]
		if event.GetId() == self.ID_AddEFolder :
			dlg = wx.TextEntryDialog(self, _("Enter new folder's name"),_('New Folder'))
			dlg.SetValue("Default")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				try:
					os.makedirs(os.path.join(base, dlg.GetValue()))
				except Exception as cond:
					wx.MessageBox(_("Can't create folder: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			dlg.Destroy()
		elif event.GetId() == self.ID_AddEPackage :
			dlg = wx.TextEntryDialog(self, _("Enter new package's name"),_('New Package'))
			dlg.SetValue("Default")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				try:
					base = os.path.join(base, dlg.GetValue())
					os.makedirs(base)
					open(os.path.join(base, '__init__.py'), 'a').close()
				except Exception as cond:
					wx.MessageBox(_("Can't create folder: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			dlg.Destroy()
		elif event.GetId() == self.ID_AddECode :
			dlg = wx.TextEntryDialog(self, _("Enter new engine's name"),_('New Engine'))
			dlg.SetValue("Default")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				try:
					base = os.path.join(base, dlg.GetValue() + '.py')
					open(base, 'a').close()
					self.CreateTextWindow(base, activate=True)
				except Exception as cond:
					wx.MessageBox(_("Can't create file: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			dlg.Destroy()
		elif event.GetId() == self.ID_ERemove :
			if os.path.isdir(base) :
				shutil.rmtree(base, True)
			else :
				os.remove(base)
		elif event.GetId() == self.ID_ImportECode :
			pkn = base.replace(Deca.world.EnginesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			if pkn.endswith('.py') :
				pkn = pkn[0:-3]
			app.log("[engines][dbg] Add code-package %s (%s)" % (pkn, base))
			ImportPackage(pkn, base, imp.PY_SOURCE)
			return # no need to rebuild tree
		elif event.GetId() == self.ID_OpenECode :
			self.CreateTextWindow(base, activate=True)
			return # no need to rebuild tree
		elif event.GetId() == self.ID_RunECode :
			fname = base.replace(Deca.world.EnginesPath, '')
			fl = None
			try:
				fl = open(base, 'r')
				exec fl in globals()
			except Exception as cond:
				wx.MessageBox(_("Error execution %s!\n%s") % (fname, cond), _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
				self.LogMessage("[exec][err] %s" % cond)
			finally:
				if fl : fl.close()
			return # no need to rebuild tree
		elif event.GetId() == self.ID_ReloadEPackage :
			pkn = base.replace(Deca.world.EnginesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			app.log("[engines][dbg] Add package %s (%s)" % (pkn, base))
			ImportPackage(pkn, base)
			return # no need to rebuild tree
		Deca.world.Modified = True
		self.UpdateWorldTree(mode=self.updateTree_Engines)

	def OnReportMenu(self,event):
		base = self.explorer.GetPyData(self.explorer.GetSelection())
		base = base[10:]
		if event.GetId() == self.ID_AddRFolder :
			dlg = wx.TextEntryDialog(self, _("Enter new folder's name"),_('New Folder'))
			dlg.SetValue("Default")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				try:
					os.makedirs(os.path.join(base, dlg.GetValue()))
				except Exception as cond:
					wx.MessageBox(_("Can't create folder: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			dlg.Destroy()
		elif event.GetId() == self.ID_AddRCode :
			dlg = wx.TextEntryDialog(self, _("Enter new report's name"),_('New Report'))
			dlg.SetValue("Default")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				try:
					base = os.path.join(base, dlg.GetValue() + '.xml')
					open(base, 'a').close()
					self.CreateTextWindow(base, ScEditor.EditorPanel.ED_TypeReport, activate=True)
				except Exception as cond:
					wx.MessageBox(_("Can't create file: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
			dlg.Destroy()
		elif event.GetId() == self.ID_RRemove :
			if os.path.isdir(base) :
				shutil.rmtree(base, True)
			else :
				os.remove(base)
		elif event.GetId() == self.ID_RGenerate :
			gen = ReportGenerator(fileName=base)
			gen.Generate(self)
		Deca.world.Modified = True
		self.UpdateWorldTree(mode=self.updateTree_Reports)

	def OnLayerMenu(self, event):
		base = self.explorer.GetItemText(self.explorer.GetSelection())
		if event.GetId() == self.ID_RemoveLayer :
			if  wx.MessageBox(_("""Are you sure to clear this layer?
NOTE: this operation can't be undone!
All data owned by this layer will be lost!"""), _("Sampo Framework"), wx.YES_NO | wx.ICON_WARNING) == wx.YES :
				# close layer page if open
				for i in range(self.nbook.GetPageCount()) :
					if self.nbook.GetPage(i).Tag == 'Graph' and self.nbook.GetPageText(i) == base:
						self.nbook.DeletePage(i)
						break
				# destroy layer
				Deca.world.DeleteLayer(base)
				# refresh view
				self.UpdateWorldTree(self.updateTree_Layers)
			# end if answer == YES
		# end if event == ID_RemoveLayer
		pass

	def SetStatus(self, text, number=0):
		self.SetStatusText(text, number)

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
		self.tb2 = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize, aui.AUI_TB_HORZ_LAYOUT)
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
			self.log('[AddUserTool][warn] Tool ID=%s already exists' % tool_id)
			self.tb2.DeleteTool(tool_id)
		self.tb2.AddTool(tool_id, '', img, img, wx.ITEM_NORMAL,
						short, long, tool_id)
		self.Bind(wx.EVT_MENU, handler, id=tool_id)
		self.log('[AddUserTool][dbg] Tool ID=%s binded' % tool_id)

# -----------------------------------------------------------------
# main Application class
# -----------------------------------------------------------------

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
		frame = PyAUIFrame(None, wx.ID_ANY, "Sampo Framework", size=(750, 570))
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

	def AddMessageCatalog(self, name, path):
		"""Add a catalog lookup path to the app
		@param name: name of catalog (i.e 'projects')
		@param path: catalog lookup path

		"""
		if self.locale is not None:
			path = resource_filename(path, 'locale')
			self.locale.AddCatalogLookupPathPrefix(path)
			self.locale.AddCatalog(name)

if __name__ == '__main__':
	app = RunApp("Sampo")
	app.MainLoop()
