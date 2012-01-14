# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ScGraph
# Purpose:     Implements panel (child window) with the graph visualizer
#
# Author:      Stinger
#
# Created:     18.10.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import imp
import wx
import wx.lib.agw.aui as aui
import Deca
import NxLayout
from Deca.Utility import CompileCode, ImportPackage, GetModule
from Deca.Object import DecaTemplate, DecaShape
from wx.lib import ogl
import DefaultShape
from FilterDlg import LayerFilterDlg, ReflectionFilterDlg
from NbookPanel import NbookPanel
from ObjectUI import ObjDialog, CreateBrush, ReflectObjDlg, CreatePen #, SaveBrush, SavePen
from EditLinks import EdtLinks, LinksDlg
from Editra.src import ed_glob
import gettext
_ = gettext.gettext

def CreateObjectShape(width = 100, height = 50, baseObj=None, template=None):
	shapeMod = None
	shapePkg = None
	if baseObj and baseObj.Graphics:
		shapePkg = baseObj.Graphics
	elif template:
		shapePkg = template
	if shapePkg:
		shapeMod = GetModule(shapePkg)
		if not shapeMod:
			ImportPackage(shapePkg, os.path.join(Deca.world.ShapesPath, shapePkg + '.py'), imp.PY_SOURCE)
			shapeMod = GetModule(shapePkg)
	if not shapeMod:
		shape = DefaultShape.ObjectShape(width, height, baseObj)
	else:
		shape = shapeMod.__dict__['ObjectShape'](width, height, baseObj)
	return shape

###########################################################################
## Class ShapeEvtHandler
###########################################################################
class LinkLine(ogl.LineShape):
	def __init__(self):
		super(LinkLine, self).__init__()

	def DrawRegion(self, dc, region, x, y):
		"""Format one region at this position."""
		if self.GetDisableLabel():
			return

		label = region.GetFormattedText()

		# First, clear a rectangle for the text IF there is any
		if len(label):
			dc.SetPen(self.GetBackgroundPen())
			dc.SetBrush(self.GetBackgroundBrush())

			# Now draw the text
			if region.GetFont():
				dc.SetFont(region.GetFont())

			for txt in label:
				txent = dc.GetTextExtent(txt.GetText())
				# Get offset from x, y
				xx, yy = region.GetPosition()

				xp = x + xx
				yp = y + yy
				dc.DrawRectangle(xp - txent[0] / 2.0, yp - txent[1] / 2.0, txent[0], txent[1])

				if self._pen:
					dc.SetPen(self._pen)
				dc.SetTextForeground(region.GetActualColourObject())

				dc.DrawText(txt.GetText(), xp - txent[0] / 2.0, yp - txent[1] / 2.0)

###########################################################################
## Class ShapeEvtHandler
###########################################################################
class LineEvtHandler(ogl.ShapeEvtHandler):
	def __init__(self, log, frame):
		ogl.ShapeEvtHandler.__init__(self)
		self.log = log
		self.statbarFrame = frame
		self._scripts = {}
		self.last_x = self.last_y = None
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
			#self.statbarFrame.propgrid.SetPropObject(shape)
			canvas.Selection.append(shape)

			if toUnselect:
				for s in toUnselect:
					s.Select(False, dc)
					canvas.Selection = [x for x in canvas.Selection if x != s]

				##canvas.Redraw(dc)
				canvas.Refresh(False)
		pass

	def OnRightClick(self, x, y, *dontcare):
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		shp = canvas.storage.graph_data[shape.GetRegionName()]
		self.last_x = x
		self.last_y = y

		cntxMenu = wx.Menu()
		cntxMenu.Tag = self
		it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE1, _("Spline mode"), wx.EmptyString, wx.ITEM_CHECK ) )
		if shp.spline:
			it.Check(True)
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE2, _("Add control point"), wx.EmptyString, wx.ITEM_NORMAL ))
		it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE3, _("Del control point"), wx.EmptyString, wx.ITEM_NORMAL ))
		if getattr(shp, 'ControlPoints', 2) < 3:
			it.Enable(False)
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_VIEW_DETAILS, _("Edit properties"), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendSeparator()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_DELETE, _("Delete"), wx.EmptyString, wx.ITEM_NORMAL ))
		# append scripts if any
		pt = wx.Point(int(x), int(y))
		pt.x *= canvas.GetScaleX()
		pt.y *= canvas.GetScaleY()
		canvas.PopupMenu( cntxMenu, pos=pt )
		pass

	def OnMenu(self, event):
		evt_id = event.GetId()
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		shp = canvas.storage.graph_data[shape.GetRegionName()]
		#lnk = canvas.GetLinks(lambda l: l.ID == shp.ID)
		if evt_id == wx.ID_FILE1:
			shp.spline = not shp.spline
			shape.SetSpline(shp.spline)
			canvas.Modified = True
		if evt_id == wx.ID_FILE2:
			shape.InsertLineControlPoint()
			shp.CPArray = shape.GetLineControlPoints()
			canvas.Modified = True
		if evt_id == wx.ID_FILE3:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		if evt_id == wx.ID_VIEW_DETAILS:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		elif evt_id == wx.ID_DELETE:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		pass
	
###########################################################################
## Class ShapeEvtHandler
###########################################################################
class ShapeEvtHandler(ogl.ShapeEvtHandler):
	def __init__(self, log, frame):
		ogl.ShapeEvtHandler.__init__(self)
		self.log = log
		self.statbarFrame = frame
		self._scripts = {}
		#self.Bind(wx.EVT_MENU, self.OnMenu)

	def UpdateStatusBar(self, shape, txt = ''):
		x, y = shape.GetX(), shape.GetY()
		width, height = shape.GetBoundingBoxMax()
		self.statbarFrame.SetStatus("Pos: (%d, %d)  Size: (%d, %d) %s" %
										(x, y, width, height, txt), 1)

	def OnLeftClick(self, x, y, keys=0, attachment=0):
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		dc = wx.ClientDC(canvas)
		canvas.PrepareDC(dc)

		if shape.Selected():
			shape.Select(False, dc)
			canvas.Selection.remove(shape)
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
						if s in canvas.Selection: canvas.Selection.remove(s)

					##canvas.Redraw(dc)
					canvas.Refresh(False)

		self.UpdateStatusBar(shape, "Selected: %i" % len(canvas.Selection))

	def OnLeftDoubleClick(self, x, y, keys = 0, attachment = 0):
		self.EditObject()

	def EditObject(self) :
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		obj = canvas.GetObject(shape.GetRegionName())
		if obj:
			dlg = ObjDialog(self.statbarFrame)
			# fill the dialog
			dlg.AddChoice(wx.ArtProvider_GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16, 16)),
							obj.TemplateName, None)
			if obj.IsReflection:
				dlg.chReflection.Value = True
			dlg.AppendRows(len(obj.Attributes))
			x = 0
			dlg.SetEditMode()
			for k,v in obj.Attributes.items():
				dlg.attrGrid.SetRowLabelValue(x, '')
				if k == obj.TitleAttr:
					dlg.attrGrid.SetRowLabelValue(x, '*')
					dlg.TitlePos = x
					dlg.stTitle.Label = _("Title attribute: %s") % k
				dlg.attrGrid.SetCellValue(row=x, col=0, s=k)
				dlg.attrGrid.SetCellValue(row=x, col=1, s=v)
				x += 1
			if not dlg.shapeSel.SetStringSelection(str(obj.Graphics)):
				dlg.shapeSel.SetSelection(0)
			# show dialog
			if dlg.ShowModal() == wx.ID_OK:
				obj.Attributes.clear()
				for x in xrange(dlg.attrGrid.GetNumberRows()) :
					nm = dlg.attrGrid.GetCellValue(row=x, col=0)
					vl = dlg.attrGrid.GetCellRawValue(row=x, col=1)
					obj.Attributes[nm] = vl
				if dlg.TitlePos > -1:
					obj.TitleAttr = dlg.attrGrid.GetCellValue(row=dlg.TitlePos, col=0)
				# update vision
				obj.Graphics = dlg.GetShapeName()
				shape.Update()
				canvas.GetParent().UpdateView(None)
			dlg.FixGrid()
			dlg.Destroy()
		pass

	def OnEndDragLeft(self, x, y, keys=0, attachment=0):
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		ogl.ShapeEvtHandler.OnEndDragLeft(self, x, y, keys, attachment)

		if not shape.Selected():
			self.OnLeftClick(x, y, keys, attachment)

		limx = shape.GetX() + shape.GetWidth()
		limy = shape.GetY() + shape.GetHeight()
		limx = max(canvas.maxWidth, limx)
		limy = max(canvas.maxHeight, limy)
		canvas.SetViewSize(limx, limy)

		objID = shape.GetRegionName()
		canvas.storage.graph_data[objID].xpos = shape.GetX()
		canvas.storage.graph_data[objID].ypos = shape.GetY()
		shape.Update()
		canvas.Modified = True
		Deca.world.Modified = True
		self.UpdateStatusBar(shape)

	def OnSizingEndDragLeft(self, pt, x, y, keys, attch):
		ogl.ShapeEvtHandler.OnSizingEndDragLeft(self, pt, x, y, keys, attch)
		shape = self.GetShape()
		canvas = shape.GetCanvas()
		shape.Recentre(self.GetShape().GetCanvas())

		limx = shape.GetX() + shape.GetWidth()
		limy = shape.GetY() + shape.GetHeight()
		limx = max(canvas.maxWidth, limx)
		limy = max(canvas.maxHeight, limy)
		canvas.SetViewSize(limx, limy)

		objID = shape.GetRegionName()
		canvas.storage.graph_data[objID].width = shape.GetWidth()
		canvas.storage.graph_data[objID].height = shape.GetHeight()
		shape.Update()
		canvas.Modified = True
		Deca.world.Modified = True
		self.UpdateStatusBar(self.GetShape())


	def OnMovePost(self, dc, x, y, oldX, oldY, display):
		shape = self.GetShape()
		ogl.ShapeEvtHandler.OnMovePost(self, dc, x, y, oldX, oldY, display)
		self.UpdateStatusBar(shape)
		if "wxMac" in wx.PlatformInfo:
			shape.GetCanvas().Refresh(False)

	def OnRightClick(self, x, y, *dontcare):
		self._scripts.clear()
		shape = self.GetShape()
		canvas = shape.GetCanvas()

		cntxMenu = wx.Menu()
		cntxMenu.Tag = self
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_EDIT, _("Attributes"), wx.EmptyString, wx.ITEM_NORMAL ) )
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_SETUP, _("Draw options"), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendSeparator()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_COPY, _("Create reflection"), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_VIEW_DETAILS, _("Edit links"), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendSeparator()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_DELETE, _("Delete"), wx.EmptyString, wx.ITEM_NORMAL ))
		# append scripts if any
		obj = canvas.GetObject(shape.GetRegionName())
		if obj:
			pl = obj.GetEngines()
			if len(pl):
				cntxMenu.AppendSeparator()
				item_id = wx.ID_HIGHEST + 1
				for fp in pl:
					item =  wx.MenuItem( cntxMenu, item_id, fp, wx.EmptyString, wx.ITEM_NORMAL )
					self._scripts[item_id] = fp
					cntxMenu.AppendItem(item)
					item_id += 1
				# foreach script
			# if any scripts found
		# if DecaObject
		pt = wx.Point(int(x), int(y))
		pt.x *= canvas.GetScaleX()
		pt.y *= canvas.GetScaleY()
		canvas.PopupMenu( cntxMenu, pos=pt )
		pass

	def OnMenu(self, event):
		evt_id = event.GetId()
		if evt_id == wx.ID_EDIT:
			self.EditObject()
		elif evt_id == wx.ID_SETUP:
			wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		elif evt_id == wx.ID_COPY:
			dlg = ReflectObjDlg(self.statbarFrame)
			if dlg.ShowModal() == wx.ID_OK:
				lName = dlg.comboLayer.GetValue().strip()
				if lName != '':
					rlayer = Deca.world.GetLayer(lName)
					shape = self.GetShape()
					canvas = shape.GetCanvas()
					obj = canvas.GetObject(shape.GetRegionName())
					if obj: obj.ReflectTo(rlayer)
				# if name given
			# fi dialog ok
		elif evt_id == wx.ID_VIEW_DETAILS:
			dlg = EdtLinks(self.statbarFrame)
			# fill up the dialog
			shape = self.GetShape()
			canvas = shape.GetCanvas()
			obj = canvas.GetObject(shape.GetRegionName())
			dlg.SetEditObject(canvas, obj)
			if dlg.ShowModal() == wx.ID_OK:
				canvas.GetParent().UpdateView(None)
			# if dialog ok
		elif evt_id == wx.ID_DELETE:
			shape = self.GetShape()
			canvas = shape.GetCanvas()
			obj = canvas.GetObject(shape.GetRegionName())
			if obj:
				if wx.MessageBox(_("Are you shure to delete object %s") % obj.GetTitle(), _("Sampo Framework"), wx.YES_NO | wx.ICON_WARNING) == wx.YES :
					canvas.RemoveObject(obj)
		elif evt_id > wx.ID_HIGHEST:
			item = self._scripts.get(evt_id)
			if item :
				dict = globals()
				shape = self.GetShape()
				canvas = shape.GetCanvas()
				obj = canvas.GetObject(shape.GetRegionName())
				try:
					obj.ExecuteEngine(item, canvas, shape, dict)
				except Exception as cond:
					self.statbarFrame.log("[LayerView ObjectEngine][err] %s" % cond)
		pass

###########################################################################
## Class LayerView
###########################################################################
class LayerView(ogl.ShapeCanvas, Deca.Layer):
	def __init__(self, parent, layerName, frame): #, log, frame
		ogl.ShapeCanvas.__init__(self, parent)
		Deca.Layer.__init__(self, Deca.world, layerName)

		self.log = wx.GetApp().GetLog()
		self.frame = frame
		self.Selection = []
		self._scripts = {}
		self.last_x = self.last_y = 0

		wid = 200
		hei = 200
		if '@view' in self.storage.graph_data.keys():
			wid = self.storage.graph_data['@view'].width
			hei = self.storage.graph_data['@view'].height
		else:
			shi = DecaShape('@view')
			shi.Tag = '@view'
			shi.width = wid
			shi.height = hei
			shi.scale = 1.0
			self.storage.graph_data['@view'] = shi
		sc = getattr(self.storage.graph_data['@view'], 'scale', 1.0)
		self.SetViewSize(wid, hei)
		self.SetScale(sc, sc)

		self.SetBackgroundColour(wx.WHITE) #"LIGHT BLUE") #
		self.diagram = ogl.Diagram()
		self.SetDiagram(self.diagram)
		self.diagram.SetCanvas(self)
		self.shapes = {}
		self.pen = wx.Pen(wx.BLACK)
		self.brush = wx.Brush(wx.BLACK)
		obj_len = len(self.storage.graph_data)
		if obj_len > 1000:
			wxres = wx.MessageBox(_("View contains of %i objects? It may take awhile to draw them all.\nAre you sure to draw objects?") % obj_len,
			                      _("Sampo Framework"), wx.YES_NO|wx.ICON_QUESTION)
		else:
			wxres = wx.ID_YES
		if wxres == wx.ID_YES:
			# add objects
			self.Freeze()
			self.diagram.SetQuickEditMode(True)
			obj_curr = 2
			for oid, shp in self.storage.graph_data.items():
				if getattr(shp, 'Tag') == 'object':
					s = self.AddObjectShape(self.storage.objects[oid], shp.xpos, shp.ypos, shp)
					s.SetPen(CreatePen(getattr(shp, 'pen', ()), self.pen))
					s.SetBrush(CreateBrush(getattr(shp, 'brush', ()), self.brush))
					s.SetWidth(shp.width)
					s.SetHeight(shp.height)
					obj_curr += 1
					frame.SetStatus(_("Draw element %d/%d") % (obj_curr, obj_len), 1)
					wx.Yield()
			#add links
			for oid, shp in self.storage.graph_data.items():
				if getattr(shp, 'Tag') == 'link':
					lnk = self.GetLinks(lambda ln: ln.StartObject == shp.start and ln.FinishObject == shp.finish)
					if len(lnk) > 0:
						#lnk = lnk[0]
						lnk = self.AddLinkShape(lnk[0], shp)
						lnk.SetPen(CreatePen(getattr(shp, 'pen', ()), self.pen))
						lnk.SetBrush(CreateBrush(getattr(shp, 'brush', ()), self.brush))
						obj_curr += 1
						frame.SetStatus(_("Draw element %d/%d") % (obj_curr, obj_len), 1)
						wx.Yield()
			self.diagram.SetQuickEditMode(False)
			self.Thaw()
		# objects redraw done
		self.Bind(wx.EVT_MENU, self.OnScript)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnWheel)
		wx.CallAfter(self.Update)

	def SetViewSize(self, maxX, maxY):
		self.maxWidth  = maxX
		self.maxHeight = maxY
		self.SetScrollbars(pixelsPerUnitX=20, pixelsPerUnitY=20, noUnitsX=self.maxWidth/20, noUnitsY=self.maxHeight/20)
		if '@view' in self.storage.graph_data.keys():
			self.storage.graph_data['@view'].width = maxX
			self.storage.graph_data['@view'].height = maxY
		else:
			shi = DecaShape('@view')
			shi.Tag = '@view'
			shi.width = maxX
			shi.height = maxY
			self.storage.graph_data['@view'] = shi

	def SetScale(self, xscale, yscale):
		yscale = xscale
		super(LayerView, self).SetScale(xscale, yscale)
		if '@view' in self.storage.graph_data.keys():
			wid  = self.storage.graph_data['@view'].width * xscale
			hei = self.storage.graph_data['@view'].height * yscale
			self.SetScrollbars(pixelsPerUnitX=20, pixelsPerUnitY=20, noUnitsX=wid/20, noUnitsY=hei/20)
			self.storage.graph_data['@view'].scale = xscale

	def OnWheel(self, event):
		dir = event.GetWheelRotation()
		if event.ControlDown() :
			#zoom
			scale = getattr(self.storage.graph_data['@view'], 'scale', 1.0)
			if dir > 0:
				scale *= 1.1
			else:
				scale *= 0.9
			self.SetScale(scale, scale)
			self.Refresh()
		elif event.ShiftDown():
			# horizontal scroll
			x, y = self.GetViewStart()
			x += -10 if dir > 0 else 10
			self.Scroll(x, y)
		else:
			# vertical scroll
			dir = -1 if dir > 0 else 1
			self.ScrollLines(dir)
		pass
	
	def UpdateColors(self, stm):
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.pen.Colour = stm.GetDefaultForeColour()
		self.brush.Colour = stm.GetDefaultBackColour()
		wx.TheColourDatabase.AddColour('SampoShapeText', self.pen.Colour)
		# update colors for shapes with default attributes
		for oid, shp in self.shapes.items():
			pen = getattr(self.storage.graph_data[oid], 'pen', ())
			if not len(pen):
				shp.SetPen(self.pen)
			brush = getattr(self.storage.graph_data[oid], 'brush', ())
			if not len(brush):
				shp.SetBrush(self.brush)
		self.Refresh()

	def ClearShapes(self):
		Deca.Layer.ClearShapes(self)
		self.diagram.RemoveAllShapes()
		self.shapes.clear()

	def RemoveObject(self, obj):
		obj_id = Deca.Layer.RemoveObject(self, obj)
		shape = self.shapes[obj_id]
		# remove links
		for line in shape.GetLines():
			shape.RemoveLine(line)
			self.diagram.RemoveShape(line)
		# delete
		self.diagram.RemoveShape(shape)
		del self.shapes[obj_id]
		self.GetParent().UpdateView(None)
		return obj_id

	def RemoveLink(self, lnk):
		lid = Deca.Layer.RemoveLink(self, lnk)
		line = self.shapes[lid]
		self.diagram.RemoveShape(line)
		del self.shapes[lid]
		return lid

	def AddObjectShape(self, obj, xpos = None, ypos = None, shapeTmpl = None):
		shape = None
		if isinstance(obj, Deca.Object):
			shp = Deca.Layer.AddObjectShape(self, obj, xpos, ypos, shapeTmpl)
			if shapeTmpl:
				shape = CreateObjectShape(width=shapeTmpl.width, height=shapeTmpl.height, baseObj=obj )
			else :
				shape = CreateObjectShape(width=shp.width, height=shp.height, baseObj=obj)
			if obj.ID in self.shapes.keys():
				# remove current shape
				self.diagram.RemoveShape(self.shapes[obj.ID])
			shape.SetCanvas(self)
			shape.SetRegionName(obj.ID)
			shape.SetPen(self.pen)
			shape.SetBrush(self.brush)
			shape.AddText(obj.GetTitle())
			shape.SetTextColour('SampoShapeText')
			# perform shape placement
			shape.SetX(shp.xpos)
			shape.SetY(shp.ypos)
			# store shape
			self.shapes[obj.ID] = shape
			self.diagram.AddShape(shape)
			self.diagram.RecentreAll(self.diagram.GetCanvas())
			shape.Show(True)
			evthandler = ShapeEvtHandler(self.log, self.frame)
			evthandler.SetShape(shape)
			evthandler.SetPreviousHandler(shape.GetEventHandler())
			shape.SetEventHandler(evthandler)
			# fix view size
			limx = shape.GetX() + shape.GetWidth()
			limy = shape.GetY() + shape.GetHeight()
			limx = max(self.maxWidth, limx)
			limy = max(self.maxHeight, limy)
			self.SetViewSize(limx, limy)
			self.Modified = True
		return shape

	def AddLinkShape(self, lnk, shapeTmpl = None):
		line = None
		fromShape = self.shapes.get(lnk.StartObject)
		toShape = self.shapes.get(lnk.FinishObject)
		if fromShape and toShape:
			shp = Deca.Layer.AddLinkShape(self, lnk, shapeTmpl)
			line = LinkLine()
			line.SetCanvas(self)
			line.SetRegionName(lnk.ID)
			line.SetPen(self.pen)
			if lnk.Directional:
				line.AddArrow(ogl.ARROW_ARROW)
			elif self.GetViewOption('bidirectional', False):
				line.AddArrow(ogl.ARROW_ARROW)
				line.AddArrow(ogl.ARROW_ARROW, ogl.ARROW_POSITION_START)
			ttl = getattr(lnk, 'Title', '').strip()
			if ttl != '':
				line.AddText(ttl)
				line.SetBrush(wx.TRANSPARENT_BRUSH)
			else:
				line.SetBrush(self.brush)
			line.MakeLineControlPoints(shp.ControlPoints)
			# add CP array with coordinates
			if hasattr(shp, 'CPArray'):
				for pt in shp.CPArray[1:-1]:
					line.InsertLineControlPoint(point=pt)
			# set spline mode
			line.SetSpline(shp.spline)
			fromShape.AddLine(line, toShape)
			self.shapes[lnk.ID] = line
			self.diagram.AddShape(line)
			line.Show(True)
			evthandler = LineEvtHandler(self.log, self.frame)
			evthandler.SetShape(line)
			evthandler.SetPreviousHandler(line.GetEventHandler())
			line.SetEventHandler(evthandler)
			self.Modified = True
		# link added
		return line

	def GetShape(self, shp_id):
		if not shp_id in self.shapes.keys():
			return None
		return self.shapes[shp_id]

	def OnRightClick(self, x, y, keys = 0):
		# layer view context menu
		self._scripts.clear()
		self.last_x = x
		self.last_y = y

		cntxMenu = wx.Menu()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_REFRESH, _("Refresh"), wx.EmptyString, wx.ITEM_NORMAL ) )
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_SETUP, _("Layout"), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendSeparator()
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_ADD, _("Add object..."), wx.EmptyString, wx.ITEM_NORMAL ))
		cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_COPY, _("Create reflection"), wx.EmptyString, wx.ITEM_NORMAL ))
		# append scripts if any
		pl = self.GetEngines()
		if len(pl):
			cntxMenu.AppendSeparator()
			item_id = wx.ID_HIGHEST + 1
			for fp in pl:
				item_tag = fp
				item =  wx.MenuItem( cntxMenu, item_id, fp, wx.EmptyString, wx.ITEM_NORMAL )
				self._scripts[item_id] = item_tag
				cntxMenu.AppendItem(item)
				item_id += 1
			# foreach script
		# if any scripts found
		pt = wx.Point(int(x), int(y))
		self.PopupMenu( cntxMenu, pos=pt )
		pass

	def OnScript(self, event):
		evt_id = event.GetId()
		src = getattr(event.EventObject, 'Tag', None)
		if src: # process shape's menu and exit
			src.OnMenu(event)
			return
		if evt_id == wx.ID_REFRESH:
			self.GetParent().UpdateView(event)
		elif evt_id == wx.ID_SETUP:
			self.GetParent().OnLayout(event)
		elif evt_id == wx.ID_ADD:
			event.x = self.last_x
			event.y = self.last_y
			self.GetParent().OnNewObject(event)
		elif evt_id == wx.ID_COPY:
			dlg = ReflectionFilterDlg(self.frame)
			if dlg.ShowModal() == wx.ID_OK:
				lName = dlg.comboLayer.GetValue().strip()
				if lName != '':
					rlayer = Deca.world.GetLayer(lName)
					if dlg.chClear.GetValue() :
						rlayer.Clear()
					# compile filters
					txt = dlg.LambdaObj.GetClearText().strip()
					if txt != '' :
						flText = 'oFilter = lambda oid, obj: ' + txt
					else:
						flText = 'oFilter = None'
					flText += '\n\n'
					txt = dlg.LambdaLnk.GetClearText().strip()
					if txt != '' :
						flText += 'lFilter = lambda link: ' + txt
					else:
						flText += 'lFilter = None'
					try:
						mod = CompileCode(flText)
						self.ReflectTo(rlayer, mod.__dict__['oFilter'], mod.__dict__['lFilter'])
					except Exception as cond:
						self.log('[LayerView][err] Filtering exception: %s' % cond)
				pass
		elif evt_id > wx.ID_HIGHEST:
			item = self._scripts.get(evt_id)
			if item :
				event.x = self.last_x
				event.y = self.last_y
				dict = globals()
				dict['ActiveEvent'] = event
				try:
					self.ExecuteEngine(item, dict)
				except Exception as cond:
					self.frame.log("[LayerView][err] %s" % cond)
		pass

###########################################################################
## Class GraphPanel
###########################################################################
class GraphPanel(NbookPanel):
	"""Graph layout view for main notebook control.
	Contains local toolbar and the graph visualizer"""
	def __init__(self, title, parent, id = -1, pos = wx.DefaultPosition,
				 size = wx.DefaultSize, style = wx.TAB_TRAVERSAL|wx.NO_BORDER, name = wx.PanelNameStr):
		"""Initialize the graph view"""
		NbookPanel.__init__ ( self, parent, id, pos, size, style, name )
		self.Tag = "Graph"
		self.Title = title
		self.icon = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_LAYER), wx.ART_MENU, wx.Size(16, 16))
		self.log = wx.GetApp().GetLog()
		self.object_filter = None
		self.link_filter = None
		self._CompileFilters()

		bSizer = wx.BoxSizer( wx.VERTICAL )

		#self.mtb = wx.ToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TB_HORIZONTAL )
		self.mtb = aui.AuiToolBar(self, -1)
		self.mtb.SetToolBitmapSize(wx.Size(16,16))
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_LAYOUT), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_SETUP, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Layout"), _("Change graph layout"), None)
		self.mtb.SetToolDropDown(wx.ID_SETUP, True)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_FILTER), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_FILE1, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Filter"), _("Set filter to view"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_PREFERENCES, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Properties"), _("Layer view properties"), None)
		self.mtb.AddSeparator()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_ADD, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add object"), _("Create object on this layer"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_FORWARD), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_INDENT, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add link"), _("Create links between selected objects"), None)
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_PLUGMGR), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_MORE, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Add graphics"), _("Create graphical shape just for illustration"), None)
		self.mtb.AddSeparator()
		tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_STOP), wx.ART_MENU, wx.Size(16, 16))
		self.mtb.AddTool(wx.ID_CLEAR, '', tbmp, tbmp, wx.ITEM_NORMAL,
						_("Clear layer"), _("Remove all objects and links from layer"), None)
		self.mtb.Realize()

		bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=5 )

		self.graph = LayerView(self, self.Title, parent)
		bSizer.Add( self.graph, proportion=1, flag=wx.EXPAND |wx.ALL, border=0 )

		self.SetSizer( bSizer )
		self.Layout()

		self.Bind(wx.EVT_MENU, self.OnProperties, id=wx.ID_PREFERENCES)
		self.Bind(wx.EVT_MENU, self.UpdateView, id=wx.ID_REFRESH)
		self.Bind(wx.EVT_MENU, self.UpdateView, id=wx.ID_SETUP)
		self.Bind(aui.EVT_AUITOOLBAR_TOOL_DROPDOWN, self.OnSelectLayout, id=wx.ID_SETUP)
		self.Bind(wx.EVT_MENU, self.OnLayout, id=wx.ID_FILE2, id2=wx.ID_FILE7)
		self.Bind(wx.EVT_MENU, self.OnFilter, id=wx.ID_FILE1)
		self.Bind(wx.EVT_MENU, self.OnNewObject, id=wx.ID_ADD)
		self.Bind(wx.EVT_MENU, self.OnNewLink, id=wx.ID_INDENT)
		self.Bind(wx.EVT_MENU, self.OnClear, id=wx.ID_CLEAR)
		# todo: add graphics-only shape, not an object

	def _CompileFilters(self):
		key = self.Title + '_view_filters'
		if not key in Deca.world.Configuration.keys():
			Deca.world.Configuration[key] = ('', '')
		txt = Deca.world.Configuration[key][0].strip()
		if txt != '' :
			flText = 'oFilter = lambda oid, obj: ' + txt
		else:
			flText = 'oFilter = None'
		flText += '\n\n'
		txt = Deca.world.Configuration[key][1].strip()
		if txt != '' :
			flText += 'lFilter = lambda link: ' + txt
		else:
			flText += 'lFilter = None'
		try:
			mod = CompileCode(flText)
			self.object_filter = mod.__dict__['oFilter']
			self.link_filter = mod.__dict__['lFilter']
		except Exception as cond:
			self.log('[GraphPanel][err] Filtering exception: %s' % cond)
		pass
	
	def OnLayout(self, event):
		evt_id = event.GetId()
		old_layout = self.graph.GetViewOption('Layout', 0)
		if evt_id == wx.ID_FILE2:
			self.graph.SetViewOption('Layout', 0)
		elif evt_id == wx.ID_FILE3:
			self.graph.SetViewOption('Layout', 1)
		elif evt_id == wx.ID_FILE4:
			self.graph.SetViewOption('Layout', 2)
		elif evt_id == wx.ID_FILE5:
			self.graph.SetViewOption('Layout', 3)
		elif evt_id == wx.ID_FILE6:
			self.graph.SetViewOption('Layout', 4)
		elif evt_id == wx.ID_FILE7:
			self.graph.SetViewOption('Layout', 5)
		new_layout = self.graph.GetViewOption('Layout', 0)
		if old_layout != new_layout:
			self.UpdateView(event)
		# that's all

	def OnSelectLayout(self, event):
		if event.IsDropDownClicked():
			tb = event.GetEventObject()
			tb.SetToolSticky(event.GetId(), True)
			# create the popup menu
			cntxMenu = wx.Menu()
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE2, _("&Random layout")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE3, _("&Circular layout")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE4, _("&Shell layout")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE5, _("S&pring layout")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE6, _("Sp&ectral layout")) )
			it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_FILE7, _("&Align to grid")) )
			# line up our menu with the button
			rect = tb.GetToolRect(event.GetId())
			pt = tb.ClientToScreen(rect.GetBottomLeft())
			pt = self.ScreenToClient(pt)

			self.PopupMenu(cntxMenu, pt)
			# make sure the button is "un-stuck"
			tb.SetToolSticky(event.GetId(), False)
		else:
			self.UpdateView(event)

	def OnFilter(self, event):
		dlg = LayerFilterDlg(self)
		key = self.Title + '_view_filters'
		if not key in Deca.world.Configuration.keys():
			Deca.world.Configuration[key] = ('', '')
		dlg.LambdaObj.SetText(Deca.world.Configuration[key][0])
		dlg.LambdaLnk.SetText(Deca.world.Configuration[key][1])
		if dlg.ShowModal() == wx.ID_OK:
			Deca.world.Configuration[key] = (dlg.LambdaObj.GetClearText(), dlg.LambdaLnk.GetClearText())
			self._CompileFilters()
			self.UpdateView(event)

	def GetParams(self):
		return self.Title

	def UpdateColors(self, stm):
		self.graph.UpdateColors(stm)

	def UpdateView(self, event):
		"""Rebuild layer diagram using current layout mode and filters."""
		if event is not None:
			event.GetId()
		# draw objects
		prev_view = self.graph.storage.graph_data.copy()
		self.graph.ClearShapes()
		objlist = self.graph.GetObjects(self.object_filter)
		obj_len = len(objlist)
		self.graph.Selection = []
		if obj_len > 1000:
			wxres = wx.MessageBox(_("View contains of %i objects? It may take awhile to draw them all.\nAre you sure to draw objects?") % len(objlist),
			                      _("Sampo Framework"), wx.YES_NO|wx.ICON_QUESTION)
			if wxres == wx.NO:
				return
		oids = set()
		self.graph.SetViewSize(200, 200)
		frame = wx.GetApp().TopWindow
		obj_curr = 0
		self.graph.Freeze()
		self.graph.diagram.SetQuickEditMode(True)
		for o in objlist:
			shp = prev_view.get(o.ID)
			if shp:
				self.graph.AddObjectShape(o,shapeTmpl = shp)
			else :
				self.graph.AddObjectShape(o)
			oids.add(o.ID)
			obj_curr += 1
			frame.SetStatus(_("Draw object %d/%d") % (obj_curr, obj_len), 1)
			wx.Yield()
		# draw links
		lnklist = self.graph.GetLinks(lambda l: (l.StartObject in oids) or (l.FinishObject in oids))
		# filter links by used objects
		lnklist = Deca.Utility.Filter(self.link_filter, lnklist)
		obj_len = len(lnklist)
		obj_curr = 0
		for l in lnklist:
			self.graph.AddLinkShape(l)
			obj_curr += 1
			frame.SetStatus(_("Draw links %d/%d") % (obj_curr, obj_len), 1)
			wx.Yield()
		nxgraph = NxLayout.Deca2Nx(self.graph.storage.graph_data)
		lt_mode = self.graph.GetViewOption('Layout', 0)
		self.log("layout mode = %d" % lt_mode)
		NxLayout.Nx2Layout(nxgraph, self.graph, lt_mode)
		self.graph.diagram.SetQuickEditMode(False)
		self.graph.Thaw()
		self.graph.Update()
		frame.SetStatus("", 1)

	def OnProperties(self, event):
		wx.MessageBox(_("Not implemented yet!"), _("Sampo Framework"))
		event.GetId()

	def OnNewObject(self, event):
		if event is not None:
			event.GetId()
		dlg = ObjDialog(self)
		#dlg.AddChoice(wx.ArtProvider_GetBitmap(str(ed_glob.ID_SAMPO_EMPTY), wx.ART_MENU, wx.Size(16, 16)), '', '')
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		dlg.Repository = repo
		dlg.CurrentLayer = self.graph
		# fill templates list
		img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU, wx.Size(16, 16))
		for o in repo.GetTemplates():
			dlg.AddChoice(img, o.Name, o.ID)
		# fill objects list
		img = wx.ArtProvider_GetBitmap(str(ed_glob.ID_ATTR_TYPE), wx.ART_MENU, wx.Size(16, 16))
		for o in repo.GetObjects():
			dlg.AddChoice(img, o.GetTitle(), o.ID)
		for o in self.graph.GetObjects():
			dlg.AddChoice(img, o.GetTitle(), o.ID)
		dlg.EnableReflection()
		dlg.cbProto.Select(0)
		dlg.OnPrototype(event)
		if dlg.ShowModal() == wx.ID_OK:
			source = dlg.cbProto.GetSelection()
			if source != wx.NOT_FOUND:
				source = dlg.cbProto.GetClientData(source)
			obj = Deca.Object()
			if dlg.chReflection.Value:
				obj.ID = source
				obj.IsReflection = True
			for x in xrange(dlg.attrGrid.GetNumberRows()) :
				nm = dlg.attrGrid.GetCellValue(row=x, col=0)
				vl = dlg.attrGrid.GetCellValue(row=x, col=1)
				obj.Attributes[nm] = vl
			if dlg.TitlePos > -1:
				obj.TitleAttr = dlg.attrGrid.GetCellValue(row=dlg.TitlePos, col=0)
			obj.TemplateName = dlg.cbProto.GetString(dlg.cbProto.GetSelection())
			if obj.TemplateName == "":
				obj.TemplateName = repo.GetTemplate(repo.ID_DefaultTemplate).Name
			# attributes copied
			self.graph.AddObject(obj)
			self.graph.AddObjectShape(obj, getattr(event, 'x', None), getattr(event, 'y', None))
			self.Refresh()

			Deca.world.Modified = True
			if self.graph.propsGrid:
				self.graph.propsGrid.UpdateGrid()
		# end if wx.ID_OK
		dlg.Destroy()

	def OnNewLink(self, event):
		if event is not None:
			event.GetId()
		if not len(self.graph.Selection) :
			return
		dlg = LinksDlg(self)
		objFrom = self.graph.GetObject(self.graph.Selection[0].GetRegionName())
		for shape in self.graph.Selection[1:] :
			objTo = self.graph.GetObject(shape.GetRegionName())
			dlg.AddItem(objFrom, objTo)
		if dlg.ShowModal() == wx.ID_OK:
			direct = dlg.cbDirect.Value
			num = dlg.linksList.GetItemCount()
			for i in range(num):
				if dlg.linksList.IsChecked(i):
					self.AddLink(dlg.Items[i][0], dlg.Items[i][1], direct)
			# all items processed
			Deca.world.Modified = True
			if self.graph.propsGrid:
				self.graph.propsGrid.UpdateGrid()
		dlg.Destroy()

	def AddObject(self, source=None, reflection=False):
		repo = Deca.world.GetLayer(Deca.World.ID_Repository)
		if not source:
			reflection = False
			source = repo.GetTemplate(repo.ID_DefaultTemplate)
		if isinstance(source, DecaTemplate) :
			reflection = False
		obj = self.graph.CreateObject(source)
		if reflection:
			obj.IsReflection = reflection
			obj.ID = source.ID
		self.graph.AddObjectShape(obj)
		self.Refresh()

		Deca.world.Modified = True
		if self.graph.propsGrid:
			self.graph.propsGrid.UpdateGrid()
		return obj

	def AddLink(self, fromObj, toObj, direct=False):
		lnk = self.graph.CreateLink(fromObj, toObj, direct)
		self.graph.AddLinkShape(lnk)

		self.Refresh()
		Deca.world.Modified = True
		if self.graph.propsGrid:
			self.graph.propsGrid.UpdateGrid()
		return lnk

	def GenerateImage(self):
		# todo: create image from layer's view
		pass

	def OnClear(self, event):
		# clear layer
		event.GetId()
		if  wx.MessageBox(_("""Are you sure to clear this layer?
NOTE: this operation can't be undone!
All data owned by this layer will be lost!"""), _("Sampo Framework"), wx.YES_NO | wx.ICON_WARNING) == wx.YES :
			self.graph.Clear()
			self.UpdateView(event)
		pass
