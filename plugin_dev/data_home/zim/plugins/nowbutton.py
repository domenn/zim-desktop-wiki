#!/usr/bin/python3
# -*- coding: utf-8 -*-

from zim.gui.pageview import PageViewExtension
from zim.notebook import NotebookExtension, Path
from zim.gui.mainwindow import MainWindowExtension

from time import strftime
from datetime import datetime, timedelta
from zim.config import StringAllowEmpty

from zim.plugins import PluginClass
from zim.actions import action

import logging

logger = logging.getLogger('zim.plugins.nowbutton')

class NowButtonPlugin(PluginClass):

	plugin_info = {
		'name': _('Now Button'), # T: plugin name
		'description': _('''\
This plugin provides an easy toolbar option to append the current time to today's journal entry and
focus that page. Note that it is easy to get back to where you were due to Zim\'s built-in back-tracking
buttons.
'''), # T: plugin description
		'author': 'Robert Hailey',
		'help': 'Plugins:NowButton',
	}
	plugin_preferences = (
		('hours_past_midnight', 'int', _('Hours past Midnight'), 4, (0, 12)),
		('timestamp_format', 'string', _('Timestamp format'), '%I:%M%p -', StringAllowEmpty)
	)

	global DAY, WEEK, MONTH, YEAR # Hack - to make sure translation is loaded
	DAY = _('Day') # T: option value
	WEEK = _('Week') # T: option value
	MONTH = _('Month') # T: option value
	YEAR = _('Year') # T: option value

	# plugin_notebook_properties = (
	# 	('namespace', 'string', _('Section'), ':Journal'), # T: input label
	# 	('granularity', 'choice', _('Use a page for each'), DAY, (DAY, WEEK, MONTH, YEAR)), # T: preferences option, values will be "Day", "Month", ...
	# )
	plugin_notebook_properties = (
		('namespace', 'string', 'Page', ':Journal', StringAllowEmpty),
		# If I have only the first item in list, I get exception: to many values to unpack.
		('qq', 'string', 'Ignored', ':Q11', StringAllowEmpty)
	)


class NowBtnPageViewExtension(PageViewExtension):
	def __init__(self, plugin, pageview):
		PageViewExtension.__init__(self, plugin, pageview)
		plugin.pv = pageview

class NowBtnNotebookExtension(NotebookExtension):
	def __init__(self, plugin, notebook):
		NotebookExtension.__init__(self, plugin, notebook)

		properties = self.plugin.notebook_properties(notebook)
		plugin.p_namespace = properties['namespace']
		plugin.notebook = notebook
		logger.debug("Now Button: Journal at: " + plugin.p_namespace)
		# if path.ischild(properties['namespace']) and daterange_from_path(path):
		# 	return 'Journal'
		# else:
		# 	return None

		# self.connectto_all(
		# 	notebook, ('suggest-link', 'get-page-template', 'init-page-template')
		# )

class NowButtonMainWindowExtension(MainWindowExtension):

	uimanager_xml = '''
		<ui>
			<menubar name='menubar'>
				<menu action='tools_menu'>
					<placeholder name='plugin_items'>
						<menuitem action='now_button_clicked'/>
					</placeholder>
				</menu>
			</menubar>
			<toolbar name='toolbar'>
				<placeholder name='tools'>
					<toolitem action='now_button_clicked'/>
				</placeholder>
			</toolbar>
		</ui>
	'''

	def __init__(self, plugin, window):
		MainWindowExtension.__init__(self, plugin, window)

	@action(
		_('Log Entry'),
		icon='gtk-jump-to',
		# readonly=True,
		accelerator = '<Control><Shift>E'
	) # T: menu item
	def now_button_clicked(self):

		offset_time=datetime.today()-timedelta(hours=self.plugin.preferences['hours_past_midnight'])

		name = self.plugin.p_namespace

		ui = self.window.uimanager

		text = '\n%s ' % strftime(self.plugin.preferences['timestamp_format']).lower();
		name =  name + strftime(':%Y:%m:%d')
		path=Path(name)



		nb = self.plugin.notebook
		page = nb.get_page(path)

		#ui.append_text_to_page(path, text)

		if not page.exists():
			parsetree = nb.get_template(page)
			page.set_parsetree(parsetree)

		page.parse('wiki', text, append=True) # FIXME format hard coded ??? (this FIXME was copied from gui.__init__)
		# ui.present(path)
		nb.store_page(page)
		self.window.open_page(page)



		# Move the cursor to the end of the line that was just appended...
		textBuffer = self.plugin.pv.textview.get_buffer()

		i = textBuffer.get_end_iter();
		i.backward_visible_cursor_positions(1);
		textBuffer.place_cursor(i);
		# and finally... scroll the window all the way to the bottom.
		self.window.pageview.scroll_cursor_on_screen();

	def on_notebook_changed(self):
		return None

