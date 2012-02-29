# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        HgCommon
# Purpose:     Common (UI) operations with HG repository.
#
# Copyright:   (c) Triplika 2012
# Licence:     LGPL
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import wx
import Deca
import HgIface
from ObjectUI import UserPassDlg
from Editra.src.profiler import Profile_Get, Profile_Set
import gettext
_ = gettext.gettext

###########################################################################
## HgPush function
###########################################################################
def HgCreate(path, **argsdict):
	# src=, , passwd=argsdict.get('passwd', '')
	remote = argsdict.get('remote', '')
	username = Profile_Get('HG_USER', 'str', '')
	uname=argsdict.get('uname', '')
	if username == '' or uname != '':
		username = uname
	passwd = argsdict.get('passwd', '')
	password = Profile_Get('HG_PASSWD', 'str', '')
	if password == '' or passwd != '':
		password = passwd
	repo = HgIface.HgInter(path, src=remote, uname=username, passwd=password)
	return repo

###########################################################################
## HgPush function
###########################################################################
# todo don't forget to change default value to insecure to False
def HgPush(repo, frame, force=False, insecure=True):
	status = repo.Local
	repo.SwitchToLocal()
	message = ''
	if repo.User == '':
		dlg = UserPassDlg(frame)
		dlg.DlgLabel = _("Code repository account:")
		if dlg.ShowModal() == wx.ID_OK:
			repo.User = dlg.txtUname.GetValue()
			repo.Password = dlg.txtPassword.GetValue()
			Profile_Set('HG_USER', repo.User)
			Profile_Set('HG_PASSWD', repo.Password)
			repo.reopen()
		dlg.Destroy()
	if repo.IsWdChanged:
		dlg = wx.TextEntryDialog(frame, _("Describe revision:"), _('Commit'))
		dlg.SetValue("Auto-commit")
		if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
			message = dlg.GetValue()
			try:
				repo.commit(message)
			except Exception as cond:
				wx.GetApp().log("[SourceControl] err: %s" % cond)
			# committed
		else:
			if not status:
				repo.SwitchToRemote()
			return
	repo.SwitchToRemote()
	if repo.IsWdChanged:
		if message == '':
			dlg = wx.TextEntryDialog(frame, _("Describe revision:"),_('Commit'))
			dlg.SetValue("Auto-commit")
			if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
				message = dlg.GetValue()
			else:
				if status:
					repo.SwitchToLocal()
				return
		try:
			repo.commit(message)
		except Exception as cond:
			wx.GetApp().log("[SourceControl] err: %s" % cond)
		# committed
	# and now - time to push
	remote_repo = Profile_Get('HG_REPOSITORY')
	if remote_repo is None:
		remote_repo = repo.Repo.paths().get('default')
	if remote_repo is None:
		remote_repo = repo.Repo.paths().get('default-push')
	if remote_repo is None:
		dlg = wx.TextEntryDialog(frame, _("Code repository URL:"),_('Push'))
		if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
			remote_repo = dlg.GetValue()
			Profile_Set('HG_REPOSITORY', remote_repo)
	if remote_repo is not None:
		repo.push(remote_repo, force=force, insecure=insecure)
	if status:
		repo.SwitchToLocal()

###########################################################################
## HgSync function
###########################################################################
# todo don't forget to change default value to insecure to False
def HgSync(repo, frame, rev=None, insecure=True, do_pull=True):
	status = repo.Local
	repo.SwitchToRemote()
	if repo.User == '':
		dlg = UserPassDlg(frame)
		dlg.DlgLabel = _("Code repository account:")
		if dlg.ShowModal() == wx.ID_OK:
			repo.User = dlg.txtUname.GetValue()
			repo.Password = dlg.txtPassword.GetValue()
			Profile_Set('HG_USER', repo.User)
			Profile_Set('HG_PASSWD', repo.Password)
			repo.reopen()
		dlg.Destroy()
	# and now - time to pull
	remote_repo = Profile_Get('HG_REPOSITORY')
	if remote_repo is None:
		remote_repo = repo.Repo.paths().get('default')
	if remote_repo is None:
		remote_repo = repo.Repo.paths().get('default-push')
	if remote_repo is None:
		dlg = wx.TextEntryDialog(frame, _("Code repository URL:"),_('Push'))
		if dlg.ShowModal() == wx.ID_OK and dlg.GetValue() != '':
			remote_repo = dlg.GetValue()
			Profile_Set('HG_REPOSITORY', remote_repo)
		dlg.Destroy()
	if remote_repo is not None:
		repo.sync(remote_repo, rev=rev, insecure=insecure, do_pull=do_pull)
	if status:
		repo.SwitchToLocal()

