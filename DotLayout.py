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
import platform
import codecs

_enc = codecs.getencoder("utf-8")

def Deca2Dot(decaGraph, force=True, mode='dot'):
    wx.GetApp().log('[PyDot][dbg] build %s graph' % mode)
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
            lb = getattr(s, 'label', str(s.ID))
            if lb.strip() != '':
                if lb.find(':') > -1:
                    lb = '"%s"' % lb
                node.set('label', lb)
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

def Dot2Layout(dotcode, layerView, mode='dot'):
    G = None
    try:
        if platform.platform().lower().find('windows') != -1:
            pdex = pydot.find_graphviz()
            cmd = pdex['dot']
            if pdex.has_key(mode):
                cmd = pdex[mode]
            p = subprocess.Popen(
                [cmd, '-Txdot'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=0x08000000,
                universal_newlines=True
            )
        else:
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
        for nd in G.get_nodes():
            attrs = nd.get_attributes()
            if attrs.get('_draw_') and not attrs.get('bb'):
                nm = nd.get_name().replace('"', '')
                w = float(attrs.get('width', '"1"').replace('"', '')) * 72
                h = float(attrs.get('height', '"1"').replace('"', '')) * 72
                pos = attrs.get('pos', '"100,100"').replace('"', '')
                px,py = (float(e) for e in pos.split(','))
                x = px - xo
                y = ym - py
                # if shape
                shp = layerView.storage.graph_data.get(uuid.UUID(nm), None)
                if shp:
                    shp.xpos = x
                    shp.ypos = y
                    shp.width = w
                    shp.height = h
           # if node
        # for nodes
    except Exception as cond:
        wx.GetApp().log('[PyDot][err] Parsing error: %s' % cond)
    finally:
        layerView.Refresh()
    return G

def Layout(layerData, layerView, mode):
    dotgraph = _enc(Deca2Dot(layerData, mode=mode))[0]
    Dot2Layout(dotgraph, layerView, mode)
