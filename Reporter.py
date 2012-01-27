# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Name:        Reporter
# Purpose:     builds reports for Sampo Framework
#
# Author:      Stinger
#
# Created:     07.11.2011
# Copyright:   (c) Stinger 2011
# Licence:     Private
#----------------------------------------------------------------------------
#!/usr/bin/python
import wx
import xml.dom.minidom
from Editra.src.eclib import choicedlg

import gettext
_ = gettext.gettext

"""Reporter module
This module provides report building abilities for the Framework.
It uses functionality provided by Deca structure.
Report builds by XML-based template, wich consis of two parts:
1) data generators
2) visualization schema

On the first stage intermediate XML file created. This file accumulate data from generators and is the formalized report representation. Python code fragments are used to generate data and Deca World's engines may be called on this stage. Also set of standard functions may be called to generate data, such as:
*) Graphical layer representation
*) Attributes set for any part of Deca structure

Report template may contains more than one visualisation schemas. Each schema produce visualisation for one output format. 

Template schema:
<report name="">
	<user-vars>
		<variable name="" prompt="" type="text|choice|multichoice|yes_no" src="text|code|engine">source</variable>
	</user-vars>
	<generators>
		<generate vriable="varname"></generate>
		...
	</generators>
	<visualisation output="rtf|html|pdf|text|etc">
	</visualisation>
</report>
"""

class ReportGenerator:
	def __init__(self, fileName=None, stringData=None):
		self.template = None
		self.name = ''
		self.varViews = {}
		self.varDict = {}
		self.output = {}
		self.generators = None
		if fileName:
			self.template = xml.dom.minidom.parse(fileName)
		elif stringData:
			self.template = xml.dom.minidom.parse(stringData)
		else:
			raise Exception, _("ReportGenerator: template must be gve by file or string representation")
		if self.template.documentElement.tagName == 'report':
			self.name = self.template.documentElement.attributes.get('name').value.strip()
		for section in self.template.documentElement.childNodes:
			if isinstance(section, xml.dom.minidom.Element):
				if section.tagName == 'user-vars':
					self._ParseVars(section)
				elif section.tagName == 'generators':
					self.generators = section
				elif section.tagName == 'visualisation':
					oname = section.attributes.get('output').value.strip()
					self.output[oname] = section
		pass

	def _ParseVars(self, section):
		for varDef in section.childNodes:
			if isinstance(varDef, xml.dom.minidom.Element):
				vname = varDef.attributes.get('name').value.strip()
				if vname != '':
					self.varViews[vname] = varDef
					self.varDict[vname] = None
		pass

	def Generate(self, parent):
		if not self.template:
			wx.messageBox(_("Report template doesn given! Nothing to generate."),
							_("Sampo Framework"), wx.OK|wx.ICON_WARNING)
			return
		# ask for the vars
		for vName in self.varViews:
			varDef = self.varViews[vName]
			vtype = varDef.attributes.get('type').value.strip()
			vsrc = varDef.attributes.get('src')
			if vsrc:
				vsrc = vsrc.value.strip()
			vprompt = varDef.attributes.get('prompt')
			if vprompt:
				vprompt = vprompt.value.strip()
			vtitle = _('Variable: %s') % vName
			if vtype == 'text':
				dlg = wx.TextEntryDialog(parent, vprompt, vtitle)
				if dlg.ShowModal() == wx.ID_OK:
					self.varDict[vName] = dlg.GetValue()
			elif vtype == 'yes_no':
				self.varDict[vName] = wx.MessageBox(vprompt, vtitle, wx.YES_NO|wx.ICON_QUESTION)
			elif vtype == 'choice':
				#dlg = wx.SingleChoiceDialog(parent, vprompt, vtitle, self._GenerateList(varDef))
				dlg = choicedlg.ChoiceDialog(parent, msg=vprompt, title=vtitle, choices=self._GenerateList(varDef))
				if dlg.ShowModal() == wx.ID_OK and dlg.Selection > -1:
					self.varDict[vName] = self.output[dlg.StringSelection]
			elif vtype == 'multichoice':
				choises = self._GenerateList(varDef)
				dlg = wx.MultiChoiceDialog(parent, vprompt, vtitle, choises)
				if dlg.ShowModal() == wx.ID_OK:
					chl = dlg.Selections
					self.varDict[vName] = [choises[x] for x in chl]
		# select output method
		outopts = self.output.keys()
		dlg = wx.SingleChoiceDialog(parent, _("Select output format for this report:"), _("Report generation"), outopts)
		if dlg.ShowModal() == wx.ID_OK and dlg.Selection > -1:
			format = self.output[dlg.StringSelection]
			wx.MessageBox(dlg.StringSelection, "Reporter")
		# build report
		self._CollectData()
		self._ProduceReport()
		pass

	def GenerateQuite(self, varDict, output):
		if not self.template:
			wx.messageBox(_("Report template doesn given! Nothing to generate."),
							_("Sampo Framework"), wx.OK|wx.ICON_WARNING)
			return
		self.varDict = varDict
		pass

	def _CollectData(self):
		pass

	def _ProduceReport(self):
		pass

	def _GenerateList(self, node):
		return []