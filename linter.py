import os
import sublime
import sublime_plugin
import platform
import subprocess
from SublimeLinter.lint import NodeLinter

# TODO: Properly export these in SL core: https://github.com/SublimeLinter/SublimeLinter/issues/1713
from SublimeLinter.lint.linter import PermanentError
from SublimeLinter.lint.base_linter.node_linter import read_json_file

is_windows = platform.system() == 'Windows'
startup_info = None
if is_windows:
	startup_info = subprocess.STARTUPINFO()
	startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

STANDARD_SELECTOR = 'source.js'
PLUGINS = {
	'eslint-plugin-html': 'text.html',
	'eslint-plugin-json': 'source.json',
	'eslint-plugin-markdown': 'text.html.markdown',
	'eslint-plugin-svelte3': 'text.html',
	'eslint-plugin-vue': 'text.html.vue',
	'@typescript-eslint/parser': 'source.ts',
}
OPTIMISTIC_SELECTOR = ', '.join({STANDARD_SELECTOR} | set(PLUGINS.values()))

settings = None

def plugin_loaded():
	global settings
	settings = sublime.load_settings('SublimeLinterContribXO.sublime-settings')

class XO(NodeLinter):
	npm_name = 'xo'
	cmd = ('xo', '--stdin', '--reporter', 'compact', '--filename', '${file}')
	regex = (
		r'^.+?: line (?P<line>\d+), col (?P<col>\d+), '
		r'(?:(?P<error>Error)|(?P<warning>Warning)) - '
		r'(?P<message>.+)'
		r' \((?P<code>.+)\)$'
	)
	defaults = {
		'selector': OPTIMISTIC_SELECTOR,
		'disable_if_not_dependency': True
	}

	def run(self, cmd, code):
		XO.ensure_plugin_installed(self, True)
		return super().run(cmd, code)

	@staticmethod
	def ensure_plugin_installed(self, isLinter) -> bool:
		# If the user changed the selector, we take it as is.
		if isLinter and self.settings['selector'] != OPTIMISTIC_SELECTOR:
			return True

		# Happy path.
		if self.view.match_selector(0, STANDARD_SELECTOR):
			return True

		# If we're here we must be pessimistic.

		# The `project_root` has the relevant `package.json` file colocated.
		# If we fallback to a global installation there is no `project_root`,
		# t.i. no auto-selector in that case as well.
		project_root = self.context.get('project_root')
		if project_root:
			# We still need to be careful, in case SublimeLinter deduced a `project_root`
			# without checking for the `package.json` explicitly. Basically, a
			# happy path for SublimeLinter core.
			manifest_file = os.path.join(project_root, 'package.json')
			try:
				manifest = read_json_file(manifest_file)
			except Exception:
				pass
			else:
				defined_plugins = PLUGINS.keys() & (
					manifest.get('dependencies', {}).keys()
					| manifest.get('devDependencies', {}).keys()
				)
				selector = ', '.join(PLUGINS[name] for name in defined_plugins)
				if selector and self.view.match_selector(0, selector):
					return True

		# Indicate an error which usually can only be solved by changing
		# the environment. Silently, do not notify and disturb the user!
		self.notify_unassign()
		raise PermanentError()

def guess_cwd(view):
	if view.file_name():
		return os.path.dirname(view.file_name())
	elif len(view.window().folders()):
		return view.window().folders()[0]

def run_cmd(cmd, data, view):
	cwd = guess_cwd(view)
	if isinstance(data, str):
		data = data.encode()

	proc = subprocess.Popen(
		cmd,
		stdin=subprocess.PIPE,
		stderr=subprocess.PIPE,
		stdout=subprocess.PIPE,
		cwd=cwd,
		startupinfo=startup_info,
	)
	stdout, stderr = proc.communicate(data)

	return stdout

def xo_fix(view, content):
	encoding = view.encoding()
	if encoding == 'Undefined':
		encoding = 'utf-8'

	cmd = settings.get('cmd', ['xo', '--stdin', '--fix'])
	code = run_cmd(cmd, content, view)
	return code.decode(encoding)

class XofixCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		return XO.ensure_plugin_installed(self, False)

	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)

		replacement = xo_fix(self.view, content)
		if content != replacement:
			self.view.replace(edit, region, replacement)

class XofixListener(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		if not settings.get('fix_on_save', False):
			return
		view.run_command('xofix')
