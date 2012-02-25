# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        DotLayout
# Purpose:     Implements graph layout algorithms using Graphviz package
#
# Copyright:   (c) Triplika 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import Deca
import uuid
import pydot
import subprocess

def Deca2Dot(decaGraph, force=True, mode='dot'):
    G = pydot.Graph()
    G.set('layout', mode)
    G.set('overlap', False)
    for s in decaGraph.values():
        tag = getattr(s, 'Tag', '')
        if s.Tag == 'object':
            node = pydot.Node(str(s.ID))
            if not force:
                node.set('pos', "%f,%f" % (s.xpos,s.ypos))
            node.set('width', float(s.width) / 72)
            node.set('height', float(s.height) / 72)
            node.set('label', getattr(s, 'label', str(s.ID)))
            G.add_node(node)
        if s.Tag == 'link':
            st = str(s.start)
            fn = str(s.finish)
            lnk = pydot.Edge(st, fn)
            if s.direct:
                lnk.set('dir', 'forward')
            if hasattr(s, 'label') and s.label != '':
                lnk.set('label', s.label)
            G.add_edge(lnk)
    return G.to_string()

def Dot2Layout(dotcode, layerView):
    G = None
    try:
        p = subprocess.Popen(
            ['dot', '-Txdot'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            universal_newlines=True
        )
        xdotcode, error = p.communicate(dotcode)
        if p.returncode == 0:
            G = pydot.graph_from_dot_data(xdotcode)
        else:
            raise Exception, error
    except Exception as cond:
        wx.GetApp().log('[PyDot][err] Processing error: %s' % cond)
    if G is None:
        return
    bb = G.get_bb()
    if bb is None or bb == '':
        return
    try:
        xo,yo,xm,ym = (float(e) for e in bb.replace('"','').split(','))
        layerView.SetViewSize(xm - xo, ym - yo)
        dc = wx.ClientDC(layerView)
        layerView.PrepareDC(dc)
        ii = 0
        for nd in G.get_nodes():
            attrs = nd.get_attributes()
            if attrs.get('_draw_') and not attrs.get('bb'):
                nm = nd.get_name().replace('"', '')
                shp = layerView.shapes.get(uuid.UUID(nm), None)
                w = float(attrs.get('width', '"1"').replace('"', '')) * 72
                h = float(attrs.get('height', '"1"').replace('"', '')) * 72
                pos = attrs.get('pos', '"100,100"').replace('"', '')
                px,py = (float(e) for e in pos.split(','))
                if shp:
                    x = px - xo
                    y = ym - py
                    shp.Move(dc, x, y)
                # if shape
                shp = layerView.storage.graph_data.get(uuid.UUID(nm), None)
                if shp:
                    shp.xpos = x
                    shp.ypos = y
           # if node
        # for nodes
    except Exception as cond:
        wx.GetApp().log('[PyDot][err] Parsing error: %s' % cond)
    finally:
        layerView.Refresh()
    return G
