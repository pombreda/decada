# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        Logger
# Purpose:     Logging abilities for the framework
#
# Copyright:   (c) Triplika 2011
# Licence:     LGPL
#-------------------------------------------------------------------------------
import os
import sys
import re
import wx

LOG_AUTO  = 6
LOG_TRACE = 5
LOG_DEBUG = 4
LOG_INFO  = 3
LOG_WARN  = 2
LOG_ERROR = 1
LOG_FATAL = 0

class Log:
	def __init__(self, frame = None) :
		self.Frame = frame
		self.filters = []
		self.AddFilter('^\[ed_txt\]')
		self.AddFilter('^\[pycomp\]')
		self.Level = LOG_TRACE

	def WriteText(self, text, level=LOG_AUTO):
		for rx in self.filters:
			if re.search(rx, text) != None:
				return
		if text[-1:] == '\n':
			text = text[:-1]
		if level == LOG_AUTO:
			# perform level auto detection
			if re.search('\[trace\]', text, re.I) != None:
				level = LOG_TRACE
			elif re.search('\[dbg\]|\[debug\]', text, re.I) != None:
				level = LOG_DEBUG
			elif re.search('\[info\]', text, re.I) != None:
				level = LOG_INFO
			elif re.search('\[warn\]|\[warning\]', text, re.I) != None:
				level = LOG_WARN
			elif re.search('\[err\]|\[error\]', text, re.I) != None:
				level = LOG_ERROR
			elif re.search('\[fatal\]', text, re.I) != None:
				level = LOG_FATAL
			pass
		else:
			# prepend message with level info
			if level >= LOG_TRACE:
				text = '[TRACE]'  + text
			elif level == LOG_DEBUG:
				text = '[DEBUG]'  + text
			elif level == LOG_INFO:
				text = '[INFO]'  + text
			elif level == LOG_WARN:
				text = '[WARN]'  + text
			elif level == LOG_ERROR:
				text = '[ERROR]'  + text
			elif level == LOG_FATAL:
				text = '[FATAL]'  + text
		if level > self.Level:
			return
		wx.LogMessage(text)
		try:
			if self.Frame is not None:
				self.Frame.LogMessage(text)
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
