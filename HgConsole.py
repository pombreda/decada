# -*- coding: utf-8 -*- 
#-------------------------------------------------------------------------------
# Name:        HgConsole
# Purpose:     Console window to operate with HG repository by raw commands
#
# Copyright:   (c) Triplika 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
import wx
from wx.lib.agw import aui
from Editra.src import ed_glob
#from Editra.src.profiler import Profile_Get, Profile_Set
#from ObjectUI import UserPassDlg
import Deca
from subprocess import *
import gettext
_ = gettext.gettext

###########################################################################
## Class HgConsole
###########################################################################

class HgConsole ( wx.Panel ):
    ID_RepoMode = wx.NewId()

    def __init__( self, parent ):
        wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.TAB_TRAVERSAL )

        self.proc = None
        self.history = []
        self.history_pos = len(self.history)
        bSizer = wx.BoxSizer( wx.VERTICAL )

        self._localBmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_COMPUTER), wx.ART_MENU, wx.Size(16, 16))
        self._localBmpGr = self._localBmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
        self._remoteBmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_WEB), wx.ART_MENU, wx.Size(16, 16))
        self._remoteBmpGr = self._remoteBmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
        self._repoModeLocal = True

        self.mtb = aui.AuiToolBar(self, -1)
        self.mtb.SetToolBitmapSize(wx.Size(16,16))
        tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_STOP), wx.ART_MENU, wx.Size(16, 16))
        self.mtb.AddTool( wx.ID_CLOSE, '', tbmp, tbmp,
            wx.ITEM_NORMAL, _('Close'), _('Close console window'), None)
        self.mtb.AddSeparator()
        self.mtb.AddTool( self.ID_RepoMode, '', self._localBmp, self._localBmpGr,
            wx.ITEM_NORMAL, _('Local history'), _('Switch to remote repository'), None)
        self.mtb.AddSeparator()
        tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_DELETE_ALL), wx.ART_MENU, wx.Size(16, 16))
        self.mtb.AddTool( wx.ID_DELETE, '', tbmp, tbmp,
            wx.ITEM_NORMAL, _('Clear'), _('Clear console window'), None)
        tbmp = wx.ArtProvider_GetBitmap(str(ed_glob.ID_CANCEL), wx.ART_MENU, wx.Size(16, 16))
        gbmp = tbmp.ConvertToImage().ConvertToGreyscale().ConvertToBitmap()
        self.mtb.AddTool( wx.ID_CANCEL, '', tbmp, gbmp,
            wx.ITEM_NORMAL, _('Break'), _('Stops current operation'), None)
        self.mtb.Realize()

        self.mtb.EnableTool(wx.ID_CANCEL, False)

        bSizer.Add( self.mtb, proportion=0, flag=wx.EXPAND, border=5 )

        self.txtConsole = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
        self.txtConsole.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 76, 90, 90, False, wx.EmptyString ) )
        bSizer.Add( self.txtConsole, proportion=1, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=1 )

        bSizerCmd = wx.BoxSizer( wx.HORIZONTAL )

        self.stHG = wx.StaticText( self, wx.ID_ANY, u"HG >", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stHG.Wrap( -1 )
        bSizerCmd.Add( self.stHG, proportion=0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.txtCommand = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.txtCommand.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 76, 90, 90, False, wx.EmptyString ) )
        bSizerCmd.Add( self.txtCommand, proportion=1, flag=wx.ALL|wx.EXPAND|wx.RIGHT, border=1 )

        bSizer.Add( bSizerCmd, proportion=0, flag=wx.EXPAND, border=0 )

        self.SetSizer( bSizer )
        self.Layout()

        # Connect Events
        self.Bind( wx.EVT_IDLE, self.OnIdle )
        self.txtCommand.Bind( wx.EVT_CHAR, self.OnCmdChar )
        self.txtCommand.Bind( wx.EVT_TEXT_ENTER, self.OnCommandEnter )
        self.Bind( wx.EVT_MENU, self.OnChangeLocation, id=self.ID_RepoMode )
        self.Bind( wx.EVT_MENU, self.OnClear, id=wx.ID_DELETE )
        self.Bind( wx.EVT_MENU, self.OnClose, id=wx.ID_CLOSE )
        self.Bind( wx.EVT_MENU, self.OnBreak, id=wx.ID_CANCEL )

    def UpdateColors(self, stm):
        self.style = stm.GetCurrentStyleSetName()
        self.SetBackgroundColour(stm.GetDefaultBackColour())
        self.txtConsole.SetBackgroundColour(stm.GetDefaultBackColour())
        self.txtConsole.SetForegroundColour(stm.GetDefaultForeColour())
        fnt = self.txtConsole.GetFont()
        sz = stm.GetDefaultFont().GetPixelSize()
        fnt.SetPixelSize((sz[0] - 1, sz[1]))
        self.txtConsole.SetFont(fnt)

        self.txtCommand.SetBackgroundColour(stm.GetDefaultBackColour())
        self.txtCommand.SetForegroundColour(stm.GetDefaultForeColour())
        fnt = self.txtCommand.GetFont()
        sz = stm.GetDefaultFont().GetPixelSize()
        fnt.SetPixelSize((sz[0] - 1, sz[1]))
        self.txtCommand.SetFont(fnt)

        self.stHG.SetBackgroundColour(stm.GetDefaultBackColour())
        self.stHG.SetForegroundColour(stm.GetDefaultForeColour())
        self.Refresh()

    # Virtual event handlers, overide them in your derived class
    def OnIdle(self, event):
        event.GetId()
        tool = self.mtb.FindTool(self.ID_RepoMode)
        if not tool:
            return
        if self._repoModeLocal != Deca.world.HgRepository.Local:
            self._repoModeLocal = Deca.world.HgRepository.Local
            if self._repoModeLocal:
                tool.SetBitmap(self._localBmp)
                tool.SetDisabledBitmap(self._localBmpGr)
                tool.SetShortHelp(_('Local history'))
                tool.SetLongHelp(_('Switch to remote repository'))
            else:
                tool.SetBitmap(self._remoteBmp)
                tool.SetDisabledBitmap(self._remoteBmpGr)
                tool.SetShortHelp(_('Master repository'))
                tool.SetLongHelp(_('Switch to local repository'))
            # redraw repository
            self.txtConsole.AppendText(_('\nCurrent repository: %s\n') % tool.GetShortHelp())
            self.mtb.Update()
        # if location changed
        self.mtb.EnableTool(self.ID_RepoMode, Deca.world.HgRepository.IsOk)
        event.Skip()

    def OnCmdChar( self, event ):
        if event.KeyCode == wx.WXK_UP:
            if self.history_pos > 0:
                self.history_pos -= 1
                self.txtCommand.SetValue(self.history[self.history_pos])
        elif event.KeyCode == wx.WXK_DOWN:
            if self.history_pos < (len(self.history) - 1):
                self.history_pos += 1
                self.txtCommand.SetValue(self.history[self.history_pos])
            else:
                self.txtCommand.Clear()
        elif event.KeyCode == wx.WXK_ESCAPE:
            self.txtCommand.Clear()
        event.Skip()

    def OnCommandEnter( self, event ):
        cmd = self.txtCommand.GetValue()
        if self.history_pos != len(self.history):
            self.history.remove(cmd)
        self.history.append(cmd)
        self.history_pos = len(self.history)
        cmd = 'hg ' + cmd
        self.txtCommand.Clear()
        self.txtConsole.AppendText(cmd + '\n')
        self.mtb.EnableTool(wx.ID_CANCEL, True)
        wx.Yield()
        self.proc = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, stdin=PIPE, cwd=Deca.world.wfs)
        l = self.proc.stdout.readline()
        while l is not None :
            l = l.replace(bytes([255]), bytes([32]))
            l = l.decode("cp866")
            self.txtConsole.AppendText(l)
            x = self.proc.poll()
            if x is not None :
                rest = self.proc.stdout.readlines()
                for l in rest :
                    l = l.replace(bytes([255]), bytes([32]))
                    l = l.decode("cp866")
                    self.txtConsole.AppendText(l)
                break
            wx.Yield()
            l = self.proc.stdout.readline()
        # process finished
        self.mtb.EnableTool(wx.ID_CANCEL, False)
        self.proc = None
        event.Skip()

    def OnBreak(self, event):
        event.GetId()
        if self.proc is not None:
            self.proc.terminate()
        pass

    def OnChangeLocation( self, event ):
        if event is not None:
            event.GetId()
        tool = self.mtb.FindTool(self.ID_RepoMode)
        if not tool:
            return
        isLocal= not self._repoModeLocal
        if isLocal:
            Deca.world.HgRepository.SwitchToLocal()
        else:
            Deca.world.HgRepository.SwitchToRemote()
        # redraw repository and change button state will be performed in OnIdle

    def OnClear( self, event ):
        self.txtConsole.Clear()
        event.Skip()

    def OnClose( self, event ):
        mgr = wx.GetApp().TopWindow._mgr
        mgr.ClosePane(mgr.GetPane("hgconsole"))
        event.Skip()
