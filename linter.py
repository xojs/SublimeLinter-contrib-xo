import os
from SublimeLinter.lint import NodeLinter

# TODO Proper export these in SL core
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
		# If the user changed the selector, we take it as is
		if self.settings['selector'] != OPTIMISTIC_SELECTOR:
			return True

		# Happy path.
		if self.view.match_selector(0, STANDARD_SELECTOR):
			return True

		# If we're here we must be pessimistic.

		# The 'project_root' has the relevant 'package.json' file colocated.
		# If we fallback to a global installation there is no 'project_root',
		# t.i. no auto-selector in that case as well.
		project_root = self.context.get('project_root')
		if project_root:
			# We still need to be careful, in case SL deduced a 'project_root'
			# without checking for the 'package.json' explicitly. Basically, a
			# happy path for SL core.
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
