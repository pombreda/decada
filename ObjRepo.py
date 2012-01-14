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
import os
import uuid
import wx
import gettext
import Deca
import ShapeEditor
from Editra.src import ed_glob, ed_style
from NbookPanel import NbookPanel
from ObjectUI import ObjDialog

_ = gettext.gettext

###########################################################################
## Class TmplDialog
###########################################################################
class TmplDialog ( wx.Dialog ):

	ID_SelectShape = wx.NewId()

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Add template"), pos = wx.DefaultPosition, size = wx.Size( 416,354 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.EditMode = False

		self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )

		bSizer = wx.BoxSizer( wx.VERTICAL )

		gSizer = wx.GridSizer( 2, 2, 0, 1 )

		self.stName = wx.StaticText( self, wx.ID_ANY, _("Template name:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stName.Wrap( -1 )
		gSizer.Add( self.stName, proportion=0, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=5 )

		self.stProto = wx.StaticText( self, wx.ID_ANY, _("Prototype:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stProto.Wrap( -1 )
		gSizer.Add( self.stProto, proportion=0, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=5 )

		self.txtName = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer.Add( self.txtName, proportion=0, flag=wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, border=5 )

		cbProtoChoices = []
		self.cbProto = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, cbProtoChoices, 0 )
		self.cbProto.SetSelection( 0 )
		gSizer.Add( self.cbProto, proportion=0, flag=wx.BOTTOM|wx.EXPAND|wx.RIGHT, border=5 )

		bSizer.Add( gSizer, proportion=0, flag=wx.EXPAND, border=0 )

		self.mstAttrs = wx.StaticText( self, wx.ID_ANY, _("Attributes:"), wx.DefaultPosition, wx.DefaultSize, 0 )
		self.mstAttrs.Wrap( -1 )
		bSizer.Add( self.mstAttrs, proportion=0, flag=wx.LEFT, border=5 )

		gbSizer = wx.GridBagSizer( 0, 0 )
		gbSizer.AddGrowableCol( 0 )
		gbSizer.AddGrowableRow( 2 )
		gbSizer.SetFlexibleDirection( wx.BOTH )
		gbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.attrGrid = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

		# Grid
		self.attrGrid.CreateGrid( 0, 2 )
		self.attrGrid.EnableEditing( True )
		self.attrGrid.EnableGridLines( True )
		self.attrGrid.EnableDragGridSize( False )
		self.attrGrid.SetMargins( 0, 0 )

		# Columns
		self.attrGrid.SetColSize( 0, 130 )
		self.attrGrid.SetColSize( 1, 150 )
		self.attrGrid.EnableDragColMove( False )
		self.attrGrid.EnableDragColSize( True )
		self.attrGrid.SetColLabelSize( 30 )
		self.attrGrid.SetColLabelValue( 0, _("Attribute") )
		self.attrGrid.SetColLabelValue( 1, _("Default value") )
		self.attrGrid.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )

		# Rows
		self.attrGrid.EnableDragRowSize( True )
		self.attrGrid.SetRowLabelSize( 20 )
		self.attrGrid.SetRowLabelAlignment( horiz=wx.ALIGN_CENTRE, vert=wx.ALIGN_CENTRE )

		# Label Appearance

		# Cell Defaults
		self.attrGrid.SetDefaultCellAlignment( horiz=wx.ALIGN_LEFT, vert=wx.ALIGN_TOP )
		gbSizer.Add( self.attrGrid, pos=wx.GBPosition( 0, 0 ), span=wx.GBSpan( 3, 1 ), flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=2 )

		self.btnAdd = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_ADD), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnAdd, pos=wx.GBPosition( 0, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		self.btnDel = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REMOVE), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnDel, pos=wx.GBPosition( 1, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		self.btnSet = wx.BitmapButton( self, wx.ID_ANY, wx.ArtProvider_GetBitmap(str(ed_glob.ID_FONT), wx.ART_MENU, wx.Size(16, 16)),
									   wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		gbSizer.Add( self.btnSet, pos=wx.GBPosition( 2, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=5 )

		bSizer.Add( gbSizer, proportion=1, flag=wx.EXPAND, border=0 )

		bSizerBottom = wx.BoxSizer( wx.HORIZONTAL )

		self.stTitle = wx.StaticText( self, wx.ID_ANY, _("Title attribute: %s") % 'None', wx.DefaultPosition, wx.DefaultSize, 0 )
		self.stTitle.Wrap( -1 )
		bSizerBottom.Add( self.stTitle, proportion=1, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5 )

		shapeSelChoices = [ "DefaultShape" ]
		shapeSelChoices.extend(Deca.world.GetShapes())
		self.shapeSel = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, shapeSelChoices, 0 )
		self.shapeSel.SetSelection( 0 )
		bSizerBottom.Add( self.shapeSel, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		bSizer.Add( bSizerBottom, proportion=0, flag=wx.EXPAND, border=0 )

		dlgButtons = wx.StdDialogButtonSizer()
		self.dlgButtonsOK = wx.Button( self, wx.ID_OK )
		dlgButtons.AddButton( self.dlgButtonsOK )
		self.dlgButtonsCancel = wx.Button( self, wx.ID_CANCEL )
		dlgButtons.AddButton( self.dlgButtonsCancel )
		dlgButtons.Realize()
		bSizer.Add( dlgButtons, proportion=0, flag=wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, border=5 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.cbProto.Bind( wx.EVT_CHOICE, self.OnPrototype )
		self.btnAdd.Bind( wx.EVT_BUTTON, self.OnAdd )
		self.btnDel.Bind( wx.EVT_BUTTON, self.OnDel )
		self.btnSet.Bind( wx.EVT_BUTTON, self.OnSet )
		self.dlgButtonsOK.Bind( wx.EVT_BUTTON, self.OnOK )

		self.TitlePos = -1

	def __del__( self ):
		# Disconnect Events
		pass

	# Virtual event handlers, overide them in your derived class
	def OnPrototype( self, event ):
		event.GetId()
		ttl = self.cbProto.GetStringSelection()
		x = self.attrGrid.GetNumberRows()
		if x > 0:
			self.attrGrid.DeleteRows(0, numRows=x)
		self.TitlePos = -1
		if ttl != '':
			repo = Deca.world.GetLayer(Deca.World.ID_Repository)
			tpl = repo.GetTemplateByName(ttl)
			if tpl is not None:
				self.attrGrid.AppendRows(len(tpl.Attributes))
				x = 0
				for k,v in tpl.Attributes.items():
					self.attrGrid.SetRowLabelValue(x, '')
					if k == tpl.TitleAttr:
						self.attrGrid.SetRowLabelValue(x, '*')
						self.TitlePos = x
						self.stTitle.Label = _("Title attribute: %s") % k
					self.attrGrid.SetCellValue(x, 0, k)
					self.attrGrid.SetCellValue(x, 1, v)
					x += 1
				# end attribute scanning
				try:
					self.shapeSel.SetStringSelection(tpl.Graphics)
				except Exception:
					self.shapeSel.SetStringSelection("DefaultShape")
			# end if template exists
		# end generation

	def OnAdd( self, event ):
		event.GetId()
		self.attrGrid.AppendRows()
		pos = self.attrGrid.GetNumberRows() - 1
		if pos >= 0 :
			self.attrGrid.SetRowLabelValue(pos, '')

	def OnDel( self, event ):
		event.GetId()
		pos = self.attrGrid.GetSelectedRows()
		if len(pos) >= 0 :
			for x in pos:
				self.attrGrid.DeleteRows(x)
				if x == self.TitlePos:
					self.TitlePos = -1
					self.stTitle.Label = _("Title attribute: %s") % 'None'
				# end if Title
			# end for selected
		# end deletion

	def OnSet( self, event ):
		event.GetId()
		pos = self.attrGrid.GetSelectedRows()
		if not len(pos):
			cll = self.attrGrid.GetSelectedCells()
			if not len(cll):
				pos.append(self.attrGrid.GetGridCursorRow())
			for c in cll:
				pos.append(c.row)
		if len(pos) > 0 :
			if self.TitlePos > -1:
				self.attrGrid.SetRowLabelValue(self.TitlePos, '')
			self.TitlePos = pos[0]
			self.attrGrid.SetRowLabelValue(pos[0], '*')
			self.stTitle.Label = _("Title attribute: %s") % self.attrGrid.GetCellValue(pos[0], 0)
		# end set Title

	def OnOK( self, event ):
		event.GetId()
		ttl = str(self.txtName.Value)
		ttl = ttl.strip()
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		if ttl == '' or (not self.EditMode and ttl in repo.GetTemplatesNames()):
			self.SetReturnCode(wx.CANCEL)
			return
		self.EndModal(wx.ID_OK)
		# end

###########################################################################
## Class RepositoryPanel
###########################################################################
class RepositoryPanel(NbookPanel):
	"""Objects repository view for main notebook control.
	Contains local toolbar and the grid viewer """
	ID_RefreshPage = wx.NewId()
	ID_AddTemplate = wx.NewId()
	ID_AddObject = wx.NewId()
	ID_AddShape = wx.NewId()

	ListID_pos = 3

	def __init__(self, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		"""Initialize the repository view"""
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "Repo"
		self.Title = _("Object repository")
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_OBJECT), wx.ART_MENU, wx.Size(16, 16))

		bSizer = wx.BoxSizer( wx.VERTICAL )

		self.mtb = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.mtb.AddTool(self.ID_RefreshPage, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Refresh view"), longHelpString= _("Refresh reposytory view"))
		self.mtb.AddSeparator()
		self.mtb.AddTool(self.ID_AddTemplate, wx.ArtProvider_GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Add template"), longHelpString= _("Create new object template"))
		self.mtb.AddTool(self.ID_AddObject, wx.ArtProvider_GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Add object"), longHelpString= _("Create new object"))
		self.mtb.AddTool(self.ID_AddShape, wx.ArtProvider_GetBitmap(str(ed_glob.ID_PLUGMGR), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Add shape"), longHelpString= _("Create new shape for object's representation"))
		self.mtb.AddSeparator()
		self.mtb.AddTool(wx.ID_DELETE, wx.ArtProvider_GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Delete"), longHelpString= _("Delete selected from repository"))
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=0 )

		self.mRepoList = wx.ListCtrl( self, style=wx.LC_REPORT )
		bSizer.Add( self.mRepoList, proportion=1, flag=wx.ALL|wx.EXPAND, border=2 )

		imglist = wx.ImageList(16, 16, True, 2)
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16,16)))
		imglist.Add(wx.ArtProvider.GetBitmap(str(ed_glob.ID_PLUGMGR), wx.ART_MENU, wx.Size(16,16)))
		self.mRepoList.AssignImageList(imglist, which=wx.IMAGE_LIST_SMALL)
		self.mRepoList.InsertColumn(0, heading='', width=20)
		self.mRepoList.InsertColumn(1, heading=_('Name'), width=125)
		self.mRepoList.InsertColumn(2, heading=_('Graphics'), width=125)
		self.mRepoList.InsertColumn(3, heading=_('Information'), width=250)
		#self.mRepoList.InsertColumn(2, 'Location', width=125)
		self.UpdateView(None)

		self.SetSizer( bSizer )
		self.Layout()

		# Connect Events
		self.mRepoList.Bind( wx.EVT_LIST_COL_BEGIN_DRAG, self.OnSizeColumn )
		self.Bind(wx.EVT_MENU, self.UpdateView, id=self.ID_RefreshPage)
		self.Bind(wx.EVT_MENU, self.AddTemplate, id=self.ID_AddTemplate)
		self.Bind(wx.EVT_MENU, self.AddObject, id=self.ID_AddObject)
		self.Bind(wx.EVT_MENU, self.AddShape, id=self.ID_AddShape)
		self.Bind(wx.EVT_MENU, self.OnDelete, id=wx.ID_DELETE)
		self.Bind(wx.EVT_MENU, self.OnListDouble, id=wx.ID_EDIT)
		self.mRepoList.Bind(wx.EVT_LEFT_DCLICK, self.OnListDouble)
		self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnListMenu)

	def UpdateColors(self, stm):
		self.style = stm.GetCurrentStyleSetName()
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.mRepoList.SetBackgroundColour(stm.GetDefaultBackColour())
		self.mRepoList.SetForegroundColour(stm.GetDefaultForeColour())
		self.Refresh()

	def UpdateView(self, event):
		if event is not None:
			event.GetId()
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		self.mRepoList.DeleteAllItems()
		tlst = repo.GetTemplates()
		idx = 0
		for t in tlst:
			self.mRepoList.InsertImageStringItem(idx, label=str(t.ID), imageIndex=0)
			self.mRepoList.SetStringItem(idx, col=1, label=t.Name)
			self.mRepoList.SetStringItem(idx, col=3, label=_("Attributes: %d") % len(t.Attributes))
			#self.mRepoList.SetStringItem(idx, col=self.ListID_pos, label=str(t.ID))
			idx += 1
		# objects
		olst = repo.GetObjects()
		for o in olst:
			self.mRepoList.InsertImageStringItem(idx, label=str(o.ID), imageIndex=1)
			nm = o.GetTitle()
			self.mRepoList.SetStringItem(idx, col=1, label=nm)
			self.mRepoList.SetStringItem(idx, col=3, label=_("Template: %s; Attributes: %d") % (str(o.TemplateName), len(o.Attributes)))
			#self.mRepoList.SetStringItem(idx, col=self.ListID_pos, label=str(t.ID))
			idx += 1
		# shapes
		path = Deca.world.ShapesPath
		if not os.path.exists(path):
			os.mkdir(path)
		slst = [f for f in os.listdir(path) if os.path.splitext(f)[1].lower() == '.py']
		for s in slst:
			self.mRepoList.InsertImageStringItem(idx, label=os.path.splitext(s)[0], imageIndex=2)
			self.mRepoList.SetStringItem(idx, col=1, label=os.path.splitext(s)[0])

	# Virtual event handlers, overide them in your derived class
	def OnSizeColumn( self, event ):
		if not event.Column:
			event.Veto()

	def AddTemplate(self, event):
		event.GetId()
		dlg = TmplDialog(self)
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		dlg.cbProto.Clear()
		dlg.cbProto.Append("")
		dlg.cbProto.AppendItems(repo.GetTemplatesNames())
		# fill the choice
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			tpl = repo.AddTemplate(dlg.txtName.Value)
			for x in xrange(dlg.attrGrid.GetNumberRows()) :
				nm = dlg.attrGrid.GetCellValue(x, 0)
				vl = dlg.attrGrid.GetCellValue(x, 1)
				tpl.Attributes[nm] = vl
			if dlg.TitlePos > -1:
				tpl.TitleAttr = dlg.attrGrid.GetCellValue(dlg.TitlePos, 0)
			tpl.Graphics = dlg.shapeSel.GetStringSelection()
			repo.LazyReindex()
			self.UpdateView(None)
			if repo.propsGrid is not None :
				repo.propsGrid.UpdateGrid()
			# create folder for template's engines
			try:
				os.makedirs(os.path.join(Deca.world.EnginesPath, dlg.txtName.Value))
			except Exception as cond:
				wx.GetApp().log("[Repository][warn] Can't create folder: %s" % cond)
		dlg.Destroy()

	def AddObject(self, event):
		event.GetId()
		dlg = ObjDialog(self)
		#dlg.AddChoice(wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_EMPTY), wx.ART_MENU, wx.Size(16, 16)), '', '')
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		dlg.Repository = repo
		dlg.CurrentLayer = repo
		# fill templates list
		img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16, 16))
		for o in repo.GetTemplatesNames():
			dlg.AddChoice(img, o, o)
		# fill objects list
		img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16, 16))
		for o in repo.GetObjects():
			dlg.AddChoice(img, o.GetTitle(), o.ID)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			pass

	def AddShape(self, event):
		path = Deca.world.ShapesPath
		dlg = wx.TextEntryDialog(self, _("Enter new shape name"), _('New Shape'))
		dlg.SetValue("Default")
		if dlg.ShowModal() == wx.ID_OK :
			try:
				path = os.path.join(path, dlg.GetValue() + '.py')
				store = open(path, 'a')

				spath = wx.GetApp().curr_dir
				if spath:
					spath = os.path.join(spath, 'DefaultShape.py')
				else:
					spath = 'DefaultShape.py'
				f = open(spath, 'r')
				store.write(f.read())
				store.close()

				self._OpenShapeEditor(path)

			except Exception as cond:
				wx.MessageBox(_("Can't create shape: %s") % cond, _("Sampo Framework"), wx.OK | wx.ICON_ERROR)
		event.Skip()

	def _OpenShapeEditor(self, spath):
		nbook = wx.GetApp().TopWindow.nbook
		for i in range(nbook.GetPageCount()) :
			if nbook.GetPage(i).Tag == u"Text" and spath == nbook.GetPage(i).GetFileName():
				nbook.SetSelection(i)
				return
		pg = ShapeEditor.ShapeEdPanel(self)
		#pg.tx.UpdateAllStyles(self.style)
		pg.UpdateColors(ed_style.StyleMgr(ed_style.StyleMgr.GetStyleSheet(self.style)))
		pg.tx.LoadFile(spath)
		ttl = pg.tx.GetTitleString()
		wx.GetApp().TopWindow.AddTab(pg, ttl, active=True)
		pass
	
	def OnListDouble(self, event):
		"""Edit selected item"""
		event.GetId()
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		idx = self.mRepoList.GetFirstSelected()
		if idx > -1:
			itm = self.mRepoList.GetItem(idx)
			tp = itm.Image
			if not tp:
				# edit the template
				code = uuid.UUID(itm.GetText())
				dlg = TmplDialog(self)
				dlg.EditMode = True
				dlg.cbProto.Clear()
				dlg.cbProto.Append("")
				dlg.cbProto.AppendItems(repo.GetTemplatesNames())
				dlg.txtName.Value = self.mRepoList.GetItem(idx, 1).Text
				dlg.cbProto.StringSelection = dlg.txtName.Value
				dlg.OnPrototype(event)
				tpl = repo.GetTemplate(code)
				try:
					dlg.shapeSel.SetStringSelection(tpl.Graphics)
				except Exception:
					dlg.shapeSel.SetStringSelection("DefaultShape")
				if code == repo.ID_DefaultTemplate:
					dlg.txtName.Enabled = False
				res = dlg.ShowModal()
				if res == wx.ID_OK:
					tpl = repo.GetTemplate(code)
					tpl.Name = dlg.txtName.Value
					tpl.TitleAttr = None
					tpl.Attributes.clear()
					for x in xrange(dlg.attrGrid.GetNumberRows()) :
						nm = dlg.attrGrid.GetCellValue(x, 0)
						vl = dlg.attrGrid.GetCellValue(x, 1)
						tpl.Attributes[nm] = vl
					if dlg.TitlePos > -1:
						tpl.TitleAttr = dlg.attrGrid.GetCellValue(dlg.TitlePos, 0)
					tpl.Graphics = dlg.shapeSel.GetStringSelection()
					repo.LazyReindex()
					self.UpdateView(None)
					if repo.propsGrid is not None :
						repo.propsGrid.UpdateGrid()
				dlg.Destroy()
			elif tp == 1:
				# edit the object
				#code = uuid.UUID(itm.GetText())
				dlg = ObjDialog(self)
				dlg.AddChoice(wx.NullBitmap, '', '')
				repo = Deca.world.GetLayer(Deca.World.ID_Repository)
				# fill templates list
				img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16, 16))
				for o in repo.GetTemplatesNames():
					dlg.AddChoice(img, o, o)
				# fill objects list
				img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16, 16))
				for o in repo.GetObjects():
					dlg.AddChoice(img, o.GetTitle(), o.ID)
				res = dlg.ShowModal()
				if res == wx.ID_OK:
					pass
			elif tp == 2:
				# edit the shape
				path = Deca.world.ShapesPath
				path = os.path.join(path, itm.GetText() + '.py')
				self._OpenShapeEditor(path)
				pass
		# end of editing

	def OnListMenu(self, event):
		cntxMenu = wx.Menu()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_EDIT, _("Edit"), wx.EmptyString, wx.ITEM_NORMAL ) )
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_DELETE, _("Delete"), wx.EmptyString, wx.ITEM_NORMAL ) )
		pt = event.GetPoint()
		pt.x += event.EventObject.Position.x
		pt.y += event.EventObject.Position.y
		self.PopupMenu( cntxMenu, pos=pt )

	def OnDelete(self, event):
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		idx = self.mRepoList.GetFirstSelected()
		event.GetId()
		if idx > -1:
			itm = self.mRepoList.GetItem(idx)
			tp = itm.Image
			nm = itm.GetText()
			if not tp :
				txt = _("template")
			elif tp == 1:
				txt = _("object")
			else: #if tp == 2:
				txt = _("shape")
			if wx.MessageBox(_("Are you sure to delete %s %s") % (txt, nm), _("Sampo Framework"), wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
				if not tp :
					#delete template
					repo.RemoveTemplate(nm)
				elif tp == 1:
					#delete object
					repo.RemoveObject(nm)
				else: #if tp == 2:
					#delete shape
					fname = os.path.join(Deca.world.ShapesPath, nm + '.py')
					os.remove(fname)
			# end if deletion confirmed
			self.UpdateView(None)
		#end if item selected
