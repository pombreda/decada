# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        DefaultShape
# Purpose:     Description for the DefaultShape
#
# Author:      Stinger
#
# Created:     25.11.11
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
import os
import wx
from wx.lib import ogl
import Deca
from ShapeBase import ObjectShapeBase
import gettext
_ = gettext.gettext

__author__ = 'Stinger'

###########################################################################
## Class ObjectShape - graphical object representation
###########################################################################
class ObjectShape(ogl.RectangleShape, ObjectShapeBase) :
    def __init__(self, width = 100, height = 50, baseObj=None):
        super(ObjectShape, self).__init__(width, height)
        self.SetCornerRadius(-0.3)
        self.object = baseObj
        self.icon = None
        if baseObj and baseObj.TemplateName and baseObj.TemplateName != '':
            icoFile = os.path.join(Deca.world.PixmapsPath, baseObj.TemplateName) + '.png'
            if os.path.exists(icoFile):
                self.icon = wx.Bitmap(icoFile)
        self.propsGrid = None

    def OnDraw(self, dc):
        ogl.RectangleShape.OnDraw(self, dc)
        if self.icon:
            x = self.GetX() - self.GetWidth() / 2.0 + 4
            y = self.GetY() - self.icon.GetHeight() / 2.0
            if self.object :
                txtw = dc.GetTextExtent(self.object.GetTitle())
                x = max(x, self.GetX() - txtw[0] / 2 - self.icon.GetWidth() - 2)
                dc.DrawBitmap(self.icon, x, y, True)
            # if object defined
        # if icon defined

    def OnDrawControlPoints(self, dc):
        if not self._drawHandles:
            return
        brush = wx.Brush(self._pen.Colour)
        for control in self._controlPoints:
            control.SetPen(self._pen)
            control.SetBrush(brush)
            control.Draw(dc)

    def Update(self):
        self._regions[0].ClearText()
        if self.object:
            self.AddText(self.object.GetTitle())
        ObjectShapeBase.Update(self)
