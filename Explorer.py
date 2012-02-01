# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Explorer
# Purpose:     World explorer view for Sampo framework
#
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/python
import os
import shutil
import wx
import wx.lib.agw.aui as aui
import imp
from ScEditor import EditorPanel
from ScGraph import GraphPanel
from RepoView import RepoView
from Editra.src import ed_style
import Editra.src.ed_glob as ed_glob
import Editra.src.syntax.synglob as synglob

import Deca
from Deca.Utility import ImportPackage
import HgCommon

import gettext
import ObjRepo
from Reporter import ReportGenerator

_ = gettext.gettext

###########################################################################
## local functions
###########################################################################
def engine_image(d, f):
	if os.path.isdir(os.path.join(d, f)):
		if os.path.exists(os.path.join(os.path.join(d, f), '__init__.py')):
			# import package
			pkf = os.path.join(d, f)
			pkn = pkf.replace(Deca.world.EnginesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			wx.GetApp().log("[engines][dbg] Add package %s (%s)" % (pkn, pkf))
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

###########################################################################
## Class expPanel
###########################################################################
class expPanel ( wx.Panel ):

	updateTree_All 		= 0xFFFF
	updateTree_Layers 	= 0x0001
	updateTree_Engines 	= 0x0002
	updateTree_Reports 	= 0x0004

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
	ID_RemoveLayer = wx.NewId()
	ID_AddLayer = wx.NewId()
	ID_RefreshWorld = wx.NewId()
	ID_RefreshLayers = wx.NewId()
	ID_RefreshEngines = wx.NewId()
	ID_RefreshReports = wx.NewId()

	ID_Commit = wx.NewId()
	ID_Push = wx.NewId()
	ID_Pull = wx.NewId()
	ID_RepoView = wx.NewId()

	def __init__( self, parent, position = wx.DefaultPosition, sz = wx.Size( 324,455 ), stl = wx.TAB_TRAVERSAL ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = position, size = sz, style = stl)

		bSizer = wx.BoxSizer( wx.VERTICAL )
		self.frame = parent

		self.tb1 = aui.AuiToolBar(self, -1)
		self.tb1.SetAuiManager(self.frame._mgr)
		# tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU, wx.Size(16, 16))
		# gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		# self.tb1.AddTool( self.ID_Commit, '', tbmp, gbmp,
		# 	wx.ITEM_NORMAL, _('Commit'), _('Store version locally'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_PUSH), wx.ART_MENU, wx.Size(16, 16))
		gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self.tb1.AddTool( self.ID_Push, '', tbmp, gbmp,
			wx.ITEM_NORMAL, _('Push'), _('Save version to remote repository'), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_PULL), wx.ART_MENU, wx.Size(16, 16))
		gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self.tb1.AddTool( self.ID_Pull, '', tbmp, gbmp,
			wx.ITEM_NORMAL, _('Synchronize'), _('Update from remote repository'), None)
		self.tb1.AddStretchSpacer()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_REPOSITORY), wx.ART_MENU, wx.Size(16, 16))
		gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
		self.tb1.AddTool( self.ID_RepoView, '', tbmp, gbmp,
			wx.ITEM_NORMAL, _('Repository'), _('Explore repository'), None)
		self.tb1.Realize()

		self.FixToolsState()

		bSizer.Add( self.tb1, proportion=0, flag=wx.EXPAND, border=0 )

		self.explorer = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
		bSizer.Add( self.explorer, proportion=1, flag=wx.ALL|wx.EXPAND, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self.explorer.Bind( wx.EVT_LEFT_DCLICK, self.OnExplDouble )
		self.explorer.Bind( wx.EVT_TREE_SEL_CHANGED, self.OnExplChaged )

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

		# self.Bind(wx.EVT_MENU, self.OnCommit, id=self.ID_Commit)
		self.Bind(wx.EVT_MENU, self.OnPush, id=self.ID_Push)
		self.Bind(wx.EVT_MENU, self.OnPull, id=self.ID_Pull)
		self.Bind(wx.EVT_MENU, self.OnRepoView, id=self.ID_RepoView)

		self.Bind(wx.EVT_TREE_ITEM_MENU, self.OnViewMenu)

	def UpdateColors(self, sm):
		self.explorer.SetBackgroundColour(sm.GetDefaultBackColour())
		self.explorer.SetForegroundColour(sm.GetDefaultForeColour())

	def UpdateWorldTree(self, mode = updateTree_All):
		if mode == self.updateTree_All:
			self.explorer.DeleteAllItems()
			root = self.explorer.AddRoot("World", image=0)
			self.explorer.SetPyData(root, obj='World')
			self.frame._InitUserToolbar()
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
				self.frame._InitUserToolbar()
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
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_DECA_WORLD), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_DECA_LAYER), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_DECA_OBJECT), wx.ART_MENU, wx.Size(16,16)))
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
				self.frame.log("[engines walking][err] %s" % cond)
			self.frame._CompleteUserToolbar()
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
				self.frame.log("[reports walking][err] %s" % cond)
		# reports added
		self.explorer.Expand(root)

	def FixToolsState(self):
		tpos = 0
		tool = self.tb1.FindToolByIndex(tpos)
		while tool:
			self.tb1.EnableTool(tool.GetId(), Deca.world.HgRepository.IsOk)
			tpos += 1
			tool = self.tb1.FindToolByIndex(tpos)
		# foreach tool

	def OnRefreshWorld(self, event):
		if event.GetId() == self.ID_RefreshLayers:
			self.UpdateWorldTree(self.updateTree_Layers)
		elif event.GetId() == self.ID_RefreshEngines:
			self.UpdateWorldTree(self.updateTree_Engines)
		elif event.GetId() == self.ID_RefreshReports:
			self.UpdateWorldTree(self.updateTree_Reports)
		else:
			self.UpdateWorldTree() #self.updateTree_All

	def OnExplDouble(self, event):
		event.GetId()
		itm = self.explorer.GetSelection()
		msg = event.EventObject.GetItemText(itm)
		ttl = str(event.EventObject.GetItemPyData(itm))
		if itm.IsOk() :
			if ttl == u'Repo':
				for i in range(self.frame.nbook.GetPageCount()) :
					if self.frame.nbook.GetPage(i).Tag == u"Repo":
						self.frame.nbook.SetSelection(i)
						self.frame.nbook.GetPage(i).UpdateView(None)
						return
				pg = ObjRepo.RepositoryPanel(self)
				self.frame.AddTab(pg, pg.Title, active=True)
				sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.frame.style))
				pg.UpdateColors(sm)
			elif ttl == u'layer':
				for i in range(self.frame.nbook.GetPageCount()) :
					if self.frame.nbook.GetPage(i).Tag == 'Graph' and self.frame.nbook.GetPageText(i) == msg:
						self.frame.nbook.SetSelection(i)
						return
				pg = GraphPanel(msg, self.frame)
				self.frame.AddTab(pg, msg, active=True)
				sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.frame.style))
				pg.UpdateColors(sm)
			elif ttl.startswith('EngineCod') :
				self.frame.CreateTextWindow(ttl[10:], activate=True)
			elif ttl.startswith('ReportCod') :
				self.frame.CreateTextWindow(ttl[10:], EditorPanel.ED_TypeReport, activate=True)
			# valid item wx.MessageBox(msg, ttl, wx.OK)

	def OnExplChaged(self, event):
		event.GetId()
		itm = self.explorer.GetSelection()
		msg = event.EventObject.GetItemText(itm)
		ttl = str(event.EventObject.GetItemPyData(itm))
		if ttl == 'World' :
			self.frame.propgrid.SetPropObject(Deca.world)
		elif ttl == 'Repo':
			obj = Deca.world.GetLayer(Deca.World.ID_Repository)
			self.frame.propgrid.SetPropObject(obj)
		elif ttl == 'layer':
			obj = Deca.world.GetLayer(msg)
			self.frame.propgrid.SetPropObject(obj)

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
					self.frame.CreateTextWindow(base, activate=True)
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
			self.frame.log("[engines][dbg] Add code-package %s (%s)" % (pkn, base))
			ImportPackage(pkn, base, imp.PY_SOURCE)
			return # no need to rebuild tree
		elif event.GetId() == self.ID_OpenECode :
			self.frame.CreateTextWindow(base, activate=True)
			return # no need to rebuild tree
		elif event.GetId() == self.ID_RunECode :
			fname = base.replace(Deca.world.EnginesPath, '')
			fl = None
			try:
				fl = open(base, 'r')
				exec fl in globals()
			except Exception as cond:
				wx.MessageBox(_("Error execution %s!\n%s") % (fname, cond), _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
				self.frame.log("[exec][err] %s" % cond)
			finally:
				if fl : fl.close()
			return # no need to rebuild tree
		elif event.GetId() == self.ID_ReloadEPackage :
			pkn = base.replace(Deca.world.EnginesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			self.frame.log("[engines][dbg] Add package %s (%s)" % (pkn, base))
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
					self.frame.CreateTextWindow(base, EditorPanel.ED_TypeReport, activate=True)
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
				for i in range(self.frame.nbook.GetPageCount()) :
					if self.frame.nbook.GetPage(i).Tag == 'Graph' and self.frame.nbook.GetPageText(i) == base:
						self.frame.nbook.DeletePage(i)
						break
				# destroy layer
				Deca.world.DeleteLayer(base)
				# refresh view
				self.UpdateWorldTree(self.updateTree_Layers)
			# end if answer == YES
		# end if event == ID_RemoveLayer
		pass

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
				#pth = ttl[10:]
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

	# def OnCommit(self, evt):
	# 	if Deca.world.HgRepository.User == '':
	# 		dlg = UserPassDlg(self)
	# 		dlg.Label = _("Code repository account:")
	# 		if dlg.ShowModal() == wx.ID_OK:
	# 			Deca.world.HgRepository.User = dlg.txtUname.GetValue()
	# 			Deca.world.HgRepository.Password = dlg.txtPassword.GetValue()
	# 			Profile_Set('HG_USER', Deca.world.HgRepository.User)
	# 			Profile_Set('HG_PASSWD', Deca.world.HgRepository.Password)
	# 	dlg = wx.TextEntryDialog(self, _("Describe revision:"),_('Commit'))
	# 	dlg.SetValue("Auto-commit")
	# 	if dlg.ShowModal() == wx.ID_OK and Deca.world.HgRepository != '':
	# 		try:
	# 			Deca.world.HgRepository.SwitchToLocal()
	# 			Deca.world.HgRepository.commit(Deca.world.HgRepository)
	# 			Deca.world.HgRepository.SwitchToRemote()
	# 			Deca.world.HgRepository.commit(Deca.world.HgRepository)
	# 			Deca.world.HgRepository.push(Profile_Get('HG_REPOSITORY', ''))
	# 		except Exception as cond:
	# 			wx.GetApp().log("[SourceControl] err: %s" % cond)
	# 	evt.GetId()

	def OnPush(self, evt):
		evt.GetId()
		HgCommon.HgPush(Deca.world.HgRepository, self)

	def OnPull(self, evt):
		evt.GetId()
		HgCommon.HgSync(Deca.world.HgRepository, self)

	def OnRepoView(self, evt):
		evt.GetId()
		for i in range(self.frame.nbook.GetPageCount()) :
			if self.frame.nbook.GetPage(i).Tag == 'RepoView':
				self.frame.nbook.SetSelection(i)
				return
		pg = RepoView(self)
		self.frame.AddTab(pg, pg.Title, active=True)
		sm = ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.frame.style))
		pg.UpdateColors(sm)
