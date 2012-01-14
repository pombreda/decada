# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        SearchBar
# Purpose:     Tool bar for editor window to search text
#
# Author:      Stinger
#
# Created:     28.11.11
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
from Editra.src.ed_cmdbar import *
from Editra.src.ed_search import EdSearchCtrl
import gettext
_ = gettext.gettext

__author__ = 'Stinger'

class SearchBar(wx.PyPanel):
	"""Simple managed panel helper class that allows for adding and
	managing the position of a small toolbar like panel.
	@see: L{ControlBar}
	"""
	def __init__(self, parent, id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.TAB_TRAVERSAL|wx.NO_BORDER):
		super(SearchBar, self).__init__(parent, id, pos, size, style)

		bSizer = wx.BoxSizer( wx.HORIZONTAL )
		self.close_b = eclib.PlateButton(self, ID_CLOSE_BUTTON,
										 bmp=XButton.GetBitmap(),
										 style=eclib.PB_STYLE_NOBG)
		bSizer.Add( self.close_b, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_REGEX), wx.ART_MENU)
		rx_btn = eclib.PlateButton(self, ID_REGEX, bmp=t_bmp,
								   style=eclib.PB_STYLE_NOBG | eclib.PB_STYLE_TOGGLE ,
								   name="RegexBtn")
		rx_btn.SetToolTipString(_("Regular expression (Alt+R)"))
		bSizer.Add( rx_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_CASE), wx.ART_MENU)
		case_btn = eclib.PlateButton(self, ID_MATCH_CASE, bmp=t_bmp,
									 style=eclib.PB_STYLE_NOBG | eclib.PB_STYLE_TOGGLE,
									 name="CaseBtn")
		case_btn.SetToolTipString(_("Case sensetive (Alt+C)"))
		bSizer.Add( case_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_SAMPO_WORD), wx.ART_MENU)
		word_btn = eclib.PlateButton(self, ID_WHOLE_WORD, bmp=t_bmp,
								   style=eclib.PB_STYLE_NOBG | eclib.PB_STYLE_TOGGLE,
								   name="WordBtn")
		word_btn.SetToolTipString(_("Whole word (Alt+W)"))
		bSizer.Add( word_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		self.ctrl = EdSearchCtrl(self, wx.ID_ANY,
										   menulen=5, size=(180, -1))
		bSizer.Add( self.ctrl, proportion=1, flag=wx.EXPAND, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DOWN), wx.ART_MENU)
		next_btn = eclib.PlateButton(self, ID_SEARCH_NEXT, _("Next"),
									 t_bmp, style=eclib.PB_STYLE_NOBG,
									 name="NextBtn")
		next_btn.SetToolTipString(_("Find next (F3)"))
		bSizer.Add( next_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU)
		prev_btn = eclib.PlateButton(self, ID_SEARCH_PRE, _("Prev"),
									 t_bmp, style=eclib.PB_STYLE_NOBG,
									 name="PrevBtn")
		prev_btn.SetToolTipString(_("Find previous (Shift+F3)"))
		bSizer.Add( prev_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )

		t_bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_FIND), wx.ART_MENU)
		fa_btn = eclib.PlateButton(self, ID_FIND_ALL, _("Find All"),
								   t_bmp, style=eclib.PB_STYLE_NOBG,
								   name="FindAllBtn")
		bSizer.Add( fa_btn, proportion=0, flag=wx.ALIGN_LEFT, border=0 )
		fa_btn.Show(False) # Hide this button by default

		# HACK: workaround bug in mac control that resets size to
		#       that of the default variant after any text has been
		#       typed in it. Note it reports the best size as the default
		#       variant and causes layout issues. wxBUG
		if wx.Platform == '__WXMAC__':
			self.ctrl.SetSizeHints(minW=180, minH=16)

		self.SetSizer( bSizer )
		self.Layout()

		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_ALT, ord('R'), ID_REGEX ),
										(wx.ACCEL_ALT, ord('C'), ID_MATCH_CASE),
										(wx.ACCEL_ALT, ord('W'), ID_WHOLE_WORD),
										(wx.ACCEL_NORMAL, wx.WXK_F3, ID_SEARCH_NEXT),
										(wx.ACCEL_SHIFT, wx.WXK_F3, ID_SEARCH_PRE)
										])
		self.ctrl.SetAcceleratorTable(accel_tbl)
		# Event Handlers
		self.Bind(wx.EVT_BUTTON, self.OnButton)
		self.Bind(wx.EVT_TOGGLEBUTTON, self.OnToggleButton)
		self.Bind(wx.EVT_MENU, self.OnButton, id=ID_SEARCH_NEXT)
		self.Bind(wx.EVT_MENU, self.OnButton, id=ID_SEARCH_PRE)
		self.Bind(wx.EVT_MENU, self.OnToggleButton, id=ID_REGEX)
		self.Bind(wx.EVT_MENU, self.OnToggleButton, id=ID_MATCH_CASE)
		self.Bind(wx.EVT_MENU, self.OnToggleButton, id=ID_WHOLE_WORD)


	def OnButton(self, evt):
		e_id = evt.GetId()
		if e_id == ID_CLOSE_BUTTON:
			self.Hide()
			self.GetParent().Layout()
		elif e_id in [ID_SEARCH_NEXT, ID_SEARCH_PRE]:
			self.ctrl.DoSearch(e_id == ID_SEARCH_NEXT)
		elif e_id == ID_FIND_ALL:
			self.ctrl.FindAll()
		else:
			evt.Skip()

	def OnToggleButton(self, evt):
		e_id = evt.GetId()
		if e_id in [ID_MATCH_CASE, ID_REGEX, ID_WHOLE_WORD]:
			ctrl = self.FindWindowById(e_id)
			if ctrl:
				if not isinstance(evt.EventObject, eclib.PlateButton):
					ctrl._ToggleState()
				if e_id == ID_MATCH_CASE:
					flag = eclib.AFR_MATCHCASE
				elif e_id == ID_WHOLE_WORD:
					flag = eclib.AFR_WHOLEWORD
				else:
					flag = eclib.AFR_REGEX

				if ctrl.IsPressed():
					self.ctrl.SetSearchFlag(flag)
				else:
					self.ctrl.ClearSearchFlag(flag)
		else:
			evt.Skip()

	def NotifyOptionChanged(self, evt):
		"""Callback for L{ed_search.SearchController} to notify of update
		to the find options.
		@param evt: eclib.finddlg.FindEvent

		"""
		self.FindWindowById(ID_MATCH_CASE).SetValue(evt.IsMatchCase())
		self.FindWindowById(ID_REGEX).SetValue(evt.IsRegEx())
		self.FindWindowById(ID_WHOLE_WORD).SetValue(evt.IsWholeWord())
