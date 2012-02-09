# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        RepoOpts
# Purpose:     Options for HG repository.
#
# Copyright:   (c) Triplika 2012
# Licence:     LGPL
#-------------------------------------------------------------------------------
import wx
from Editra.src.profiler import Profile_Get, Profile_Set
import gettext
_ = gettext.gettext

###########################################################################
## Class RepoOpts
###########################################################################

class RepoOpts ( wx.Dialog ):

    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _("Repository paramenters"), pos = wx.DefaultPosition, size = wx.Size( 399,222 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU )

        self.SetSizeHintsSz( wx.DefaultSize, maxSize=wx.DefaultSize )

        bSizer = wx.BoxSizer( wx.VERTICAL )

        gbSizer = wx.GridBagSizer( 0, 0 )
        gbSizer.AddGrowableCol( 1 )
        gbSizer.AddGrowableRow( 4 )
        gbSizer.SetFlexibleDirection( wx.BOTH )
        gbSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.stURL = wx.StaticText( self, wx.ID_ANY, _("Repo URL"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stURL.Wrap( -1 )
        gbSizer.Add( self.stURL, pos=wx.GBPosition( 0, 0 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.txtURL = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.txtURL, pos=wx.GBPosition( 0, 1 ), span=wx.GBSpan( 1, 2 ), flag=wx.ALL|wx.EXPAND, border=2 )

        self.stUname = wx.StaticText( self, wx.ID_ANY, _("Username"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stUname.Wrap( -1 )
        gbSizer.Add( self.stUname, pos=wx.GBPosition( 1, 0 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.txtUname = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.txtUname, pos=wx.GBPosition( 1, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL|wx.EXPAND, border=2 )

        self.stPasswd = wx.StaticText( self, wx.ID_ANY, _("Password"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stPasswd.Wrap( -1 )
        gbSizer.Add( self.stPasswd, pos=wx.GBPosition( 2, 0 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.txtPasswd = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PASSWORD )
        gbSizer.Add( self.txtPasswd, pos=wx.GBPosition( 2, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL|wx.EXPAND, border=2 )

        self.stStatus = wx.StaticText( self, wx.ID_ANY, ("Status"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.stStatus.Wrap( -1 )
        gbSizer.Add( self.stStatus, pos=wx.GBPosition( 3, 0 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.txtStatus = wx.StaticText( self, wx.ID_ANY, _("Unknown"), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txtStatus.Wrap( -1 )
        gbSizer.Add( self.txtStatus, pos=wx.GBPosition( 3, 1 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border=5 )

        self.btnCheck = wx.Button( self, wx.ID_ANY, _("Check"), wx.DefaultPosition, wx.DefaultSize, 0 )
        gbSizer.Add( self.btnCheck, pos=wx.GBPosition( 3, 2 ), span=wx.GBSpan( 1, 1 ), flag=wx.ALL, border=2 )

        bSizer.Add( gbSizer, proportion=1, flag=wx.EXPAND, border=5 )

        sdbSizer = wx.StdDialogButtonSizer()
        self.sdbSizerOK = wx.Button( self, wx.ID_OK )
        sdbSizer.AddButton( self.sdbSizerOK )
        self.sdbSizerCancel = wx.Button( self, wx.ID_CANCEL )
        sdbSizer.AddButton( self.sdbSizerCancel )
        sdbSizer.Realize()
        bSizer.Add( sdbSizer, proportion=0, flag=wx.ALL|wx.EXPAND, border=5 )

        self.SetSizer( bSizer )
        self.Layout()

        self.Centre( wx.BOTH )

        # Connect Events
        self.btnCheck.Bind( wx.EVT_BUTTON, self.OnCheck )
        self.sdbSizerOK.Bind( wx.EVT_BUTTON, self.OnOK )

        # Fill data
        data = Profile_Get('HG_REPOSITORY', 'str', '')
        self.txtURL.SetValue(data)
        data = Profile_Get('HG_USER', 'str', '')
        self.txtUname.SetValue(data)
        data = Profile_Get('HG_PASSWD', 'str', '')
        self.txtPasswd.SetValue(data)

    # Virtual event handlers, override them in your derived class
    def OnCheck( self, event ):
        self.txtStatus.SetLabel( _("Not implemented yet"))
        event.Skip()

    def OnOK( self, event ):
        data = self.txtURL.GetValue()
        Profile_Set('HG_REPOSITORY', data)
        data = self.txtUname.GetValue()
        Profile_Set('HG_USER', data)
        data = self.txtPasswd.GetValue()
        Profile_Set('HG_PASSWD', data)
        event.Skip()
