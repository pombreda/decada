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
#!/usr/bin/env python
import wx
import wx.stc
from wx.py import shell
from Editra.src import ed_glob
from Editra.src import ed_style
from Editra.src.profiler import Profile_Get, Profile_Set
import Editra.src.syntax.syntax as syntax
import gettext

_ = gettext.gettext
__author__ = 'Stinger'
PYSHELL_STYLE = "PyShell.Style" # Profile Key

class EdPyShell(shell.Shell, ed_style.StyleMgr):
    """Custom PyShell that uses Editras StyleManager"""
    def __init__(self, parent):
        """Initialize the Shell"""
        shell.Shell.__init__(self, parent) #, locals=dict()

        # Get the color scheme to use
        style = Profile_Get(PYSHELL_STYLE)
        if style is None:
            style = Profile_Get('SYNTHEME')

        ed_style.StyleMgr.__init__(self, self.GetStyleSheet(style))

        # Attributes
        self.SetStyleBits(5)
        self._shell_style = style
        mgr = syntax.SyntaxMgr(ed_glob.CONFIG['CACHE_DIR'])
        syn_data = mgr.GetSyntaxData('py')
        synspec = syn_data.SyntaxSpec
        self.SetLexer(wx.stc.STC_LEX_PYTHON)
        self.SetSyntax(synspec)

    def GetShellTheme(self):
        """Get the theme currently used by the shell
        @return: string

        """
        return self._shell_style

    def SetShellTheme(self, style):
        """Set the color scheme used by the shell
        @param style: style sheet name (string)

        """
        self._shell_style = style
        Profile_Set(PYSHELL_STYLE, style)
        self.UpdateAllStyles(style)
