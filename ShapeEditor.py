# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ShapeEditor
# Purpose:     Code editor with some additional functions
#
# Author:      Stinger
#
# Created:     29.11.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
from Deca.Utility import *
from ScEditor import *
from wx.lib import ogl
import wx.lib.agw.aui as aui
import gettext
from ScGraph import CreateObjectShape

_ = gettext.gettext

###########################################################################
## Class ShapeEdPanel
###########################################################################
class ShapeEdPanel(EditorPanel):
	"""Tab editor view for main notebook control.
	Contains local toolbar and the editor itself """
	def __init__(self, parent, id = -1, pos = wx.DefaultPosition, size = wx.DefaultSize,
				 style = wx.TAB_TRAVERSAL, name = wx.PanelNameStr):
		"""Initialize the editor view"""
		super(ShapeEdPanel, self).__init__ ( EditorPanel.ED_TypeScript, parent, id, pos, size, style, name )
		self.Tag = "Text Shape"
		self.pane = None

		mtb = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		mtb.AddTool(wx.ID_REFRESH, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REFRESH), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Reload module"), longHelpString= _("Reload code to use"))
		mtb.AddTool(wx.ID_VIEW_DETAILS, wx.ArtProvider_GetBitmap(str(ed_glob.ID_DECA_IMAGES), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Preview"), longHelpString= _("Preview shape drawing"))
		mtb.AddSeparator()
		mtb.AddTool(wx.ID_SAVE, wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAVE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Save"), longHelpString= _("Save engine text"))
		mtb.AddTool(wx.ID_SAVEAS, wx.ArtProvider_GetBitmap(str(ed_glob.ID_NEW), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Save as..."), longHelpString= _("Save engine text as new engine"))
		mtb.AddSeparator()
		mtb.AddTool(wx.ID_UNDO, wx.ArtProvider_GetBitmap(str(ed_glob.ID_UNDO), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Undo"), longHelpString= _("Undo previous operation"))
		mtb.AddTool(wx.ID_REDO, wx.ArtProvider_GetBitmap(str(ed_glob.ID_REDO), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("Redo"), longHelpString= _("Redo reverted operation"))
		mtb.AddTool(wx.ID_PREVIEW, wx.ArtProvider_GetBitmap(str(ed_glob.ID_METHOD_TYPE), wx.ART_MENU, wx.Size(16, 16)),
						shortHelpString= _("CodeBrowser"), longHelpString= _("Toggle CodeBrowser window"))
		#self.mtb.AddLabelTool( wx.ID_ANY, _("tool"), wx.NullBitmap, wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString )
		mtb.Realize()

		self.GetSizer().Replace(self.mtb, mtb)
		self.mtb.Destroy()
		self.mtb = mtb

		self.Bind(wx.EVT_MENU, self.ReloadCode, id=wx.ID_REFRESH)
		self.Bind(wx.EVT_MENU, self.ShowPreview, id=wx.ID_VIEW_DETAILS)

	def GetParams(self):
		return os.path.basename(self.GetFileName())

	def GetShapeName(self):
		nm = self.GetFileName()
		nm = nm.replace(Deca.world.ShapesPath, '').replace(os.sep, '.')
		if nm.startswith('.'):
				nm = nm[1:]
		nm = os.path.splitext(nm)[0]
		return nm

	def UpdateColors(self, stm):
		super(ShapeEdPanel, self).UpdateColors(stm)
		self.style_mgr = stm
		pass

	def ReloadCode(self, evt):
		if evt.GetId() == wx.ID_REFRESH:
			path = self.GetFileName()
			pkn = path.replace(Deca.world.ShapesPath, '').replace(os.sep, '.')
			if pkn.startswith('.'):
				pkn = pkn[1:]
			if pkn.endswith('.py') :
				pkn = pkn[0:-3]
			ImportPackage(pkn, path, imp.PY_SOURCE)
			if self.pane and self.pane.window:
				self.pane.window.SetShape(self.GetShapeName())
		else:
			evt.Skip()

	def ShowPreview(self, evt):
		if evt.GetId() == wx.ID_VIEW_DETAILS:
			mgr = wx.GetApp().TopWindow._mgr
			self.pane = mgr.GetPane("shape_preview")
			if not self.pane.window:
				mgr.AddPane(ShapePreviewPanel(wx.GetApp().TopWindow), aui.AuiPaneInfo().
							Name("shape_preview").Caption(_("Shape preview")).
							Dockable(False).Float().Hide().CloseButton(True).MaximizeButton(True))
				self.pane = mgr.GetPane("shape_preview")
				self.pane.window.SetShape(self.GetShapeName())
			self.pane.Float().Show()
			if self.pane.floating_pos == wx.DefaultPosition:
				pt = wx.GetApp().TopWindow.ClientToScreen(wx.Point(100, 20))
				self.pane.FloatingPosition(pt)
			self.pane.window.UpdateColors(self.style_mgr)
			evt.SetId(wx.ID_REFRESH)
			self.ReloadCode(evt)
			mgr.Update()
		else:
			evt.Skip()

###########################################################################
## Class ShapePreviewPanel
###########################################################################
class ShapePreviewPanel(wx.Panel):
	"""ShapePreviewPanel is a pane for preview shape drawing"""
	def __init__(self, parent, _id = -1, pos = wx.DefaultPosition,
				 size = wx.Size( 250,240 ), style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		super(ShapePreviewPanel, self).__init__(parent, _id, pos, size, style, name)
		self.shape = None
		self.pen = wx.Pen(wx.BLACK)
		self.brush = wx.Brush(wx.BLACK)

		bSizer = wx.BoxSizer(wx.VERTICAL)

		self.diagram = ogl.ShapeCanvas(self)
		bSizer.Add(self.diagram, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)

		self.SetSizer(bSizer)
		self.Layout()

		# fix-ups for event handler
		self.diagram.Selection = []
		self.diagram.SetDiagram(ogl.Diagram())
		self.diagram.GetDiagram().SetCanvas(self.diagram)
		self.Bind(wx.EVT_SIZE, self.OnSize)

	def OnSize(self, evt):
		evt.GetId()
		self.Layout()
		pass

	def UpdateColors(self, stm):
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.diagram.SetBackgroundColour(stm.GetDefaultBackColour())
		self.pen.Colour = stm.GetDefaultForeColour()
		self.brush.Colour = stm.GetDefaultBackColour()
		wx.TheColourDatabase.AddColour('SampoShapeText', self.pen.Colour)
		# update colors for shapes with default attributes
		if self.shape:
			self.shape.SetPen(self.pen)
			self.shape.SetBrush(self.brush)
		self.diagram.Refresh()

	def SetShape(self, name):
		sz = self.diagram.GetSizeTuple()
		try:
			shp = CreateObjectShape(sz[0] - 15, sz[1] - 15, template=name)
		except Exception:
			shp = CreateObjectShape(sz[0] - 15, sz[1] - 15, template='DefaultShape')
		if shp:
			if self.shape :
				self.shape.Delete()
			# add new shape
			self.shape = shp
			self.shape.SetCanvas(self.diagram)
			self.shape.SetRegionName('')
			self.shape.SetPen(self.pen)
			self.shape.SetBrush(self.brush)
			self.shape.AddText(_('Shape preview'))
			self.shape.SetTextColour('SampoShapeText')
			# perform shape placement
			self.shape.SetX(sz[0] / 2)
			self.shape.SetY(sz[1] / 2)
			# store shape
			self.diagram.AddShape(self.shape)
			#self.diagram.GetDiagram().RecentreAll(self.diagram)
			self.shape.Show(True)
			evthandler = PreviewEvtHandler(wx.GetApp().GetLog(), wx.GetApp().TopWindow)
			evthandler.SetShape(self.shape)
			evthandler.SetPreviousHandler(self.shape.GetEventHandler())
			self.shape.SetEventHandler(evthandler)

			self.diagram.Refresh()
		pass

###########################################################################
## Class PreviewEvtHandler
###########################################################################
class PreviewEvtHandler(ogl.ShapeEvtHandler):
	def __init__(self, log, frame):
		ogl.ShapeEvtHandler.__init__(self)
		self.log = log
		self.statbarFrame = frame
		self._scripts = {}
		#self.Bind(wx.EVT_MENU, self.OnMenu)

	def OnLeftClick(self, x, y, keys=0, attachment=0):
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		dc = wx.ClientDC(canvas)
		canvas.PrepareDC(dc)

		if shape.Selected():
			shape.Select(False, dc)
			canvas.Selection = [x for x in canvas.Selection if x != shape]
			#canvas.Redraw(dc)
			canvas.Refresh(False)
		else:
			#redraw = False
			shapeList = canvas.GetDiagram().GetShapeList()
			toUnselect = []

			for s in shapeList:
				if s.Selected():
					# If we unselect it now then some of the objects in
					# shapeList will become invalid (the control points are
					# shapes too!) and bad things will happen...
					toUnselect.append(s)

			shape.Select(True, dc)
			self.statbarFrame.propgrid.SetPropObject(shape)
			canvas.Selection.append(shape)

			if (not keys & 1) and toUnselect:
					for s in toUnselect:
						s.Select(False, dc)
						canvas.Selection = [x for x in canvas.Selection if x != s]

					##canvas.Redraw(dc)
					canvas.Refresh(False)

	def OnEndDragLeft(self, x, y, keys=0, attachment=0):
		shape = self.GetShape()
		ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

		if not shape.Selected():
			self.OnLeftClick(x, y, keys, attachment)

	def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
		ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
		shape = self.GetShape()
		shape.Recentre(self.GetShape().GetCanvas())

	def OnMovePost(self, dc, x, y, oldX, oldY, display):
		shape = self.GetShape()
		ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
		if "wxMac" in wx.PlatformInfo:
			shape.GetCanvas().Refresh(False)
