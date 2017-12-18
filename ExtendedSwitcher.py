import sublime, sublime_plugin, os

class ExtendedSwitcherCommand(sublime_plugin.WindowCommand):
	# declarations
	open_files = []
	open_views = []
	window = []
	settings = []

	# lets go
	def run(self, list_mode):
		# self.view.insert(edit, 0, "Hello, World!")
		self.open_files = []
		self.open_views = []
		self.window = sublime.active_window()
		self.settings = sublime.load_settings('ExtendedSwitcher.sublime-settings')
		self.active_view = self.window.active_view()

		folders = self.window.folders()
		active_view_id = self.active_view.id()

		current_index = 0
		current_tab_index = 0

		for view in self.getViews(list_mode):
			current_index += 1
			is_current_view = view.id() == active_view_id

			# if skip the current active is enabled do not add the current file it for selection
			if self.settings.get('skip_current_file') == True:
				if is_current_view:
					continue

			self.open_views.append(view) # add the view object
			file_name = view.file_name() # get the full path
			file_path = ''

			if is_current_view:
				current_tab_index = current_index
				current_view_prefix = " (Current View)"

			else:
				current_view_prefix = ""

			if file_name:
				for folder in folders:
					if os.path.commonprefix([folder, file_name]) == folder:
						file_path = os.path.relpath(file_name, folder)

				if view.is_dirty():
					file_name += self.settings.get('mark_dirty_file_char') # if there are any unsaved changes to the file

				if self.settings.get('show_full_file_path') == True:
					self.open_files.append([os.path.basename(file_name) + current_view_prefix, file_path])
				else:
					self.open_files.append([os.path.basename(file_name) + current_view_prefix, ''])
			elif view.name():
				if view.is_dirty():
					self.open_files.append([view.name() + self.settings.get('mark_dirty_file_char') + current_view_prefix, ''])
				else:
					self.open_files.append([view.name() + current_view_prefix, ''])
			else:
				if view.is_dirty():
					self.open_files.append(["Untitled"+self.settings.get('mark_dirty_file_char') + current_view_prefix, ''])
				else:
					self.open_files.append(["Untitled" + current_view_prefix, ''])

		if current_tab_index == current_index:
			current_tab_index -= 2

		if self.check_for_sorting() == True:
			self.sort_files()

		def on_selection(selected):

			if selected > -1:
				self.window.focus_view(self.open_views[selected])

		self.window.show_quick_panel(self.open_files, self.tab_selected, 0, current_tab_index, on_selection) # show the file list

	# display the selected open file
	def tab_selected(self, selected):

		if selected > -1:
			self.window.focus_view(self.open_views[selected])

		else:
			self.window.focus_view(self.active_view)

	# sort the files for display in alphabetical order
	def sort_files(self):
		open_files = self.open_files
		open_views = []

		open_files.sort()

		for file_path in open_files:
			file_path = file_path[0]
			for fv in self.open_views:
				if fv.file_name():
					file_path = file_path.replace(" - " + os.path.dirname(fv.file_name()),'')
					if (file_path == os.path.basename(fv.file_name())) or (file_path == os.path.basename(fv.file_name())+self.settings.get('mark_dirty_file_char')):
						open_views.append(fv)
						self.open_views.remove(fv)
				elif fv.name() == file_path or fv.name()+self.settings.get('mark_dirty_file_char') == file_path:
					open_views.append(fv)
					self.open_views.remove(fv)
				elif file_path == "Untitled" and not fv.name():
					open_views.append(fv)
					self.open_views.remove(fv)

		self.open_views = open_views

	# flags for sorting
	def check_for_sorting(self):
		if self.settings.has("sort"):
			return self.settings.get("sort", False)

	def getViews(self, list_mode):
		views = []
		# get only the open files for the active_group
		if list_mode == "active_group":
			views = self.window.views_in_group(self.window.active_group())

		# get all open view if list_mode is window or active_group doesn't have any files open
		if (list_mode == "window") or (len(views) < 1):
			views = self.window.views()

		return views


