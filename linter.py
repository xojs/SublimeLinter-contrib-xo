import os
import platform
import sublime
import sublime_plugin
import subprocess
from SublimeLinter.lint import (
	NodeLinter,
	linter as linter_module
)

# TODO: Properly export these in SL core: https://github.com/SublimeLinter/SublimeLinter/issues/1713
from SublimeLinter.lint.linter import PermanentError
from SublimeLinter.lint.base_linter.node_linter import read_json_file


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

startup_info = None
if platform.system() == 'Windows':
	startup_info = subprocess.STARTUPINFO()
	startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

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
		self.ensure_plugin_installed()
		return super().run(cmd, code)

	def ensure_plugin_installed(self) -> bool:
		# If the user changed the selector, we take it as is.
		if self.settings['selector'] != OPTIMISTIC_SELECTOR:
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

def make_fake_linter(view):
	settings = linter_module.get_linter_settings(XO, view)
	return XO(view, settings)

def xo_fix(self, view, content):
	if isinstance(content, str):
		content = content.encode()

	encoding = view.encoding()
	if encoding == 'Undefined':
		encoding = 'utf-8'

	print('xo_fix -> content length:', len(content))
	print('xo_fix -> encoding:', encoding)
	print('xo_fix -> xo_start_dir:', self.xo_start_dir) # Print again just to be sure
	print('xo_fix -> xo_env.PWD:', self.xo_env['PWD'])

	# TODO: Change to use `subprocess.run()` when Sublime updates Python to 3.5 or later. 
	proc = subprocess.Popen(
		[self.xo_path, '--stdin', '--fix'],
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		env=self.xo_env,
		cwd=self.xo_start_dir,
		startupinfo=startup_info,
	)
	stdout, _ = proc.communicate(content)
	print('xo_fix -> stdout:', len(stdout))

	return stdout.decode(encoding)

class XoFixCommand(sublime_plugin.TextCommand):
	def is_enabled(self):
		print('XoFixCommand -> is_enabled?')
		linter = make_fake_linter(self.view)

		self.xo_start_dir = linter.get_start_dir()
		print('XoFixCommand -> xo_start_dir', self.xo_start_dir)
		if not self.xo_start_dir:
			print('XoFixCommand -> xo_start_dir -> False')
			return False

		self.xo_path = linter.find_local_executable(self.xo_start_dir, 'xo')
		print('XoFixCommand -> xo_path', self.xo_path)
		if not self.xo_path:
			print('XoFixCommand -> xo_path -> False')
			return False

		self.xo_env = os.environ.copy()
		self.xo_env['PWD'] = self.xo_start_dir

		print('XoFixCommand -> return -> True')
		return True

	def run(self, edit):
		region = sublime.Region(0, self.view.size())
		content = self.view.substr(region)

		replacement = xo_fix(self, self.view, content)
		if content != replacement:
			self.view.replace(edit, region, replacement)

class XoFixListener(sublime_plugin.EventListener):
	def on_pre_save(self, view):
		if not settings.get('fix_on_save', False):
			return
		view.run_command('xo_fix')
