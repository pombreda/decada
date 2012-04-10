# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Logger
# Purpose:     Logging abilities for the framework
#
# Copyright:   (c) Stinger 2011
# Licence:     Private
#-------------------------------------------------------------------------------
import os
import sys
import re
import wx
from datetime import datetime
import gettext

_ = gettext.gettext

LOG_AUTO  = 6
LOG_TRACE = 5
LOG_DEBUG = 4
LOG_INFO  = 3
LOG_WARN  = 2
LOG_ERROR = 1
LOG_FATAL = 0
LOG_LEVEL_STR = [_("[FATAL]"), _("[ERROR]"), _("[WARN]"), _("[INFO]"), _("[DEBUG]"), _("[TRACE]")]

USE_DATE_NONE  = 0
USE_DATE_SHORT = 1
USE_DATE_LONG  = 2

###########################################################################
## Class Log - logging operations
###########################################################################
class Log:
	def __init__(self, frame = None) :
		self.Frame = frame
		self.filters = []
		self.AddFilter('^\[ed_txt\]')
		self.AddFilter('^\[pycomp\]')
		self.AddFilter('^\[ed_style\]')
		self.Level = LOG_TRACE
		self.useDate = USE_DATE_SHORT

	def WriteText(self, text, level=LOG_AUTO):
		for rx in self.filters:
			if re.search(rx, text) != None:
				return
		if text[-1:] == '\n':
			text = text[:-1]
		if level == LOG_AUTO:
			# perform level auto detection
			if re.search('\[fatal\]', text, re.I) != None:
				text = re.sub('\[fatal\]', '', text, 0, re.I)
				level = LOG_FATAL
			elif re.search('\[err\]|\[error\]', text, re.I) != None:
				text = re.sub('\[err\]|\[error\]', '', text, 0, re.I)
				level = LOG_ERROR
			elif re.search('\[warn\]|\[warning\]', text, re.I) != None:
				text = re.sub('\[warn\]|\[warning\]', '', text, 0, re.I)
				level = LOG_WARN
			elif re.search('\[info\]', text, re.I) != None:
				text = re.sub('\[info\]', '', text, 0, re.I)
				level = LOG_INFO
			elif re.search('\[dbg\]|\[debug\]', text, re.I) != None:
				text = re.sub('\[dbg\]|\[debug\]', '', text, 0, re.I)
				level = LOG_DEBUG
			else: # any other cases assumed as trace
				text = re.sub('\[trace\]', '', text, 0, re.I)
				level = LOG_TRACE
				if re.search('Traceback ', text, re.I) != None:
					level = LOG_ERROR
			pass
		# prepend message with level info
		if level > LOG_TRACE or level < LOG_FATAL:
			level = LOG_TRACE
		if level > self.Level:
			return
		text = LOG_LEVEL_STR[level] + ' ' + text
		if self.useDate != USE_DATE_NONE:
			dt = unicode(datetime.now())
			if self.useDate == USE_DATE_SHORT:
				dt = dt.split('.')[0]
			text = dt + ' ' + text
		#wx.LogMessage(text)
		try:
			if self.Frame is not None:
				self.Frame.LogMessage(text, level)
		except Exception:
			pass

	def LogTrace(self, text):
		self.WriteText(text, LOG_TRACE)

	def LogDebug(self, text):
		self.WriteText(text, LOG_DEBUG)

	def LogInfo(self, text):
		self.WriteText(text, LOG_INFO)

	def LogWarn(self, text):
		self.WriteText(text, LOG_WARN)

	def LogError(self, text):
		self.WriteText(text, LOG_ERROR)

	def LogFatal(self, text):
		self.WriteText(text, LOG_FATAL)

	def AddFilter(self, pattern, flags=0):
		rx = re.compile(pattern)
		if rx is not None:
			self.filters.append(rx)
		pass

	def AddFilterText(self, text_to_skip):
		pattern = re.escape(text_to_skip)
		self.AddFilter(pattern)

	write = WriteText
	__call__ = WriteText

	def flush(self):
		pass

###########################################################################
## Class LogView - logging panel
###########################################################################
class LogView (wx.ListCtrl):
	def __init__(self, parent, wxid = wx.ID_ANY):
		wx.ListCtrl.__init__(self, parent, wxid, wx.DefaultPosition, wx.DefaultSize,
						wx.LC_NO_HEADER|wx.LC_NO_SORT_HEADER|wx.LC_REPORT|wx.LC_SINGLE_SEL )
		self.InsertColumn(col=0, heading='Text')
		self.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 76, 90, 90, False, wx.EmptyString ) )

		self.traceColor = wx.Color(0x000000) # black
		self.debugColor = wx.Color(0x000000) # black
		self.infoColor = wx.Color(0x000000) # black
		self.warnColor = wx.Color(0x000000) # black
		self.errorColor = wx.Color(0x000000) # black
		self.fatalColor = wx.Color(0x000000) # black
		self.fatalFont = self.GetFont()
		self.traceFont = self.GetFont()

		self.txtwid = 0
		self.Bind( wx.EVT_SIZE, self.OnResize)
		self.Bind( wx.EVT_RIGHT_DOWN, self.OnMenu)
		self.Bind(wx.EVT_MENU, self.OnClear, id=wx.ID_DELETE)
		self.Bind(wx.EVT_MENU, self.OnUseDate, id=wx.ID_HIGHEST + 1, id2=wx.ID_HIGHEST + 3)
		self.Bind(wx.EVT_MENU, self.OnSetLevel, id=wx.ID_HIGHEST + 10, id2=wx.ID_HIGHEST + 10 + LOG_TRACE)

	def UpdateColors(self, stm):
		cl = wx.Color()
		self.SetBackgroundColour(stm.GetDefaultBackColour())
		self.SetForegroundColour(stm.GetDefaultForeColour())
		# log entries
		sm = stm.GetItemByName('error_style')
		self.fatalColor.SetFromString(sm.fore)
		self.errorColor.SetFromString(sm.fore)
		sm = stm.GetItemByName('keyword_style')
		self.warnColor.SetFromString(sm.fore)
		sm = stm.GetItemByName('string_style')
		self.infoColor.SetFromString(sm.fore)
		sm = stm.GetItemByName('comment_style')
		self.debugColor.SetFromString(sm.fore)
		self.traceColor.SetFromString(sm.fore)
		fnt = self.GetFont()
		sz = stm.GetDefaultFont().GetPixelSize()
		fnt.SetPixelSize((sz[0] - 1, sz[1]))
		self.SetFont(fnt)
		self.fatalFont = self.GetFont()
		self.fatalFont.Weight = 92
		self.fatalFont.Style = 90
		self.traceFont = self.GetFont()
		self.traceFont.Weight = 90
		self.traceFont.Style = 94

	def LogMessage(self, text, level = LOG_AUTO):
		dc = wx.WindowDC(self)
		dc.SetFont(self.fatalFont)
		lines = text.split('\n')
		itm = -1
		for ln in lines:
			itm = self.Append([ln])
			ext = dc.GetTextExtent(ln)
			if ext[0] > self.txtwid:
				self.txtwid = ext[0]
			if level == LOG_FATAL:
				self.SetItemTextColour(itm, col=self.fatalColor)
				self.SetItemFont(itm, self.fatalFont)
			elif level == LOG_ERROR:
				self.SetItemTextColour(itm, col=self.errorColor)
			elif level == LOG_WARN:
				self.SetItemTextColour(itm, col=self.warnColor)
			elif level == LOG_INFO:
				self.SetItemTextColour(itm, col=self.infoColor)
			elif level == LOG_DEBUG:
				self.SetItemTextColour(itm, col=self.debugColor)
			elif level == LOG_TRACE:
				self.SetItemTextColour(itm, col=self.traceColor)
				self.SetItemFont(itm, self.traceFont)
		self.SetColumnWidth(0, width=self.txtwid + 20)
		if itm > -1:
			self.EnsureVisible(itm)
		pass

	def OnResize(self, evt):
		txtsz = self.GetSize()
		sz = self.txtwid
		if sz < txtsz[0]:
			sz = txtsz[0]
		self.SetColumnWidth(0, width=sz)
		evt.Skip()

	def OnClear(self, evt):
		self.DeleteAllItems()

	def OnUseDate(self, evt):
		eid = evt.GetId() - wx.ID_HIGHEST - 1
		if eid >= USE_DATE_NONE and eid <= USE_DATE_LONG:
			wx.GetApp().log.useDate = eid
		pass

	def OnSetLevel(self, evt):
		eid = evt.GetId()
		eid = eid - wx.ID_HIGHEST - 10
		if eid >= LOG_FATAL and eid <= LOG_TRACE:
			wx.GetApp().log.Level = eid
		pass

	def OnMenu(self, evt):
		_log = wx.GetApp().log
		cntxMenu = wx.Menu()
		it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_DELETE,
				_("Clear log"), wx.EmptyString, wx.ITEM_NORMAL ) )
		# date format menu
		dtmnu = wx.Menu()
		it = dtmnu.AppendItem( wx.MenuItem( dtmnu, wx.ID_HIGHEST + 1,
				_("None"), wx.EmptyString, wx.ITEM_CHECK ) )
		if _log.useDate == USE_DATE_NONE:
			it.Check(True)
		it = dtmnu.AppendItem( wx.MenuItem( dtmnu, wx.ID_HIGHEST + 2,
				_("Short form"), wx.EmptyString, wx.ITEM_CHECK ) )
		if _log.useDate == USE_DATE_SHORT:
			it.Check(True)
		it = dtmnu.AppendItem( wx.MenuItem( dtmnu, wx.ID_HIGHEST + 3,
				_("Long form"), wx.EmptyString, wx.ITEM_CHECK ) )
		if _log.useDate == USE_DATE_LONG:
			it.Check(True)
		it = cntxMenu.AppendSubMenu(dtmnu, _("Use date") )
		lvmnu = wx.Menu()
		li = LOG_TRACE
		for lv in LOG_LEVEL_STR.__reversed__():
			it = lvmnu.AppendItem( wx.MenuItem( lvmnu, wx.ID_HIGHEST + 10 + li,
					lv, wx.EmptyString, wx.ITEM_CHECK ) )
			if _log.Level == li:
				it.Check(True)
			li -= 1
		it = cntxMenu.AppendSubMenu(lvmnu, _("Logging level %s") % LOG_LEVEL_STR[_log.Level] )
		it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_SAVEAS,
				_("Export"), wx.EmptyString, wx.ITEM_NORMAL ) )
		it = cntxMenu.AppendItem( wx.MenuItem( cntxMenu, wx.ID_PREFERENCES,
				_("Settings"), wx.EmptyString, wx.ITEM_NORMAL ) )

		pt = evt.Position
		# pt.x += evt.EventObject.Position.x
		# pt.y += evt.EventObject.Position.y
		self.PopupMenu( cntxMenu, pos=pt )
