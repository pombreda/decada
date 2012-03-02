# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        NxLayout
# Purpose:     Implements graph layout algorithms usin NetworkX package
#
# Author:      Stinger
#
# Created:     25.12.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import networkx as nx
import Deca
import uuid
import numpy

def shell_layout(G):
    pos = nx.shell_layout(G)
    for p in pos.values():
        p[0] = (p[0] + 1) / 2
        p[1] = (p[1] + 1) / 2
    return pos

def grid_layout(G):
    lnodes = G.nodes(True)
    gw = G.graph.get('deca_width', 200.0)
    gh = G.graph.get('deca_height', 200.0)
    bw = float(G.graph.get('deca_shape_w', 0.0)) / 2
    bh = float(G.graph.get('deca_shape_h', 0.0)) / 2
    nnum = len(lnodes)
    width = round(numpy.sqrt(nnum))
    hstep = 1.0 / width
    vstep = 1.0 / ((nnum / width) + 1)
    pos = {}
    xpos = ypos = 0.0
    for n in lnodes:
        x = (n[1].get('xpos', 0.0) - bw) / gw
        y = (n[1].get('ypos', 0.0) - bh) / gh
        x /= hstep
        y /= vstep
        x = round(x) * hstep
        y = round(y) * vstep
        pos[n[0]] = numpy.ndarray((2,), buffer=numpy.array([x, y]))
    # all nodes processed
    return pos

__layout_func__ = [nx.random_layout, nx.circular_layout, shell_layout,
                   nx.spring_layout, nx.spectral_layout, grid_layout]

def Deca2Nx(decaGraph):
    G = nx.MultiDiGraph()
    maxX = maxY = 0
    maxH = maxW = 0
    for s in decaGraph.values():
        tag = getattr(s, 'Tag', '')
        if s.Tag == 'object':
            G.add_node(str(s.ID),xpos=s.xpos,ypos=s.ypos)
            maxX = max(maxX, s.xpos)
            maxY = max(maxY, s.ypos)
            maxW = max(maxW, s.width)
            maxH = max(maxH, s.height)
        if s.Tag == 'link':
            st = str(s.start)
            fn = str(s.finish)
            G.add_edge(st,fn)
    G.graph['deca_width'] = maxX
    G.graph['deca_height'] = maxY
    G.graph['deca_shape_w'] = maxW
    G.graph['deca_shape_h'] = maxH
    return G

def Nx2Layout(nx_graph, layerView, pos=None):
    vw = nx_graph.graph['deca_width']
    bw = nx_graph.graph['deca_shape_w']
    vh = nx_graph.graph['deca_height']
    bh = nx_graph.graph['deca_shape_h']
    if not pos:
        pos = nx.random_layout(nx_graph)
    if type(pos) == int:
        if pos < 0 or pos >= len(__layout_func__):
            pos = 0
        pos = __layout_func__[pos](nx_graph)
    layerView.SetViewSize(vw + bw, vh + bh)
    bw /= 2
    bh /= 2
    for obj,coord in pos.items():
        #wx.GetApp().log("[Nx2Layout][dbg] %s: %s" % (obj,coord))
        x = vw * coord[0] + bw
        y = vh * coord[1] + bh
        shp = layerView.storage.graph_data.get(uuid.UUID(obj), None)
        if shp:
            shp.xpos = x
            shp.ypos = y

def Layout(layerData, layerView, mode):
    nxgraph = Deca2Nx(layerData)
    Nx2Layout(nxgraph, layerView, mode)
