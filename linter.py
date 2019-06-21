import sublime, sublime_plugin, subprocess, os, os.path, sys
from SublimeLinter.lint import NodeLinter

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
CODE_DIRS = [
  'plugin_helpers'
]
sys.path += [BASE_PATH] + [os.path.join(BASE_PATH, f) for f in CODE_DIRS]

from plugin_helpers.utils import memoize

class SettingManager(object):
    @memoize
    def _user_settings():
        return sublime.load_settings('SublimeLinterContribXO.sublime-settings')

    @memoize
    def get_setting(name, default=None):
        v = SettingManager._user_settings().get(name)
        if v == None:
            try:
                return sublime.active_window().active_view().settings().get(name, default)
            except AttributeError:
                # No view defined.
                return default
        else:
            return v

CMD_XO = SettingManager.get_setting('xo_cmd', 'xo')

class XO(NodeLinter):
    cmd = (CMD_XO, '--stdin', '--reporter', 'compact', '--filename', '${file}')
    regex = (
        r'^.+?: line (?P<line>\d+), col (?P<col>\d+), '
        r'(?:(?P<error>Error)|(?P<warning>Warning)) - '
        r'(?P<message>.+)'
        r' \((?P<code>.+)\)$'
    )
    defaults = {
        'selector': 'source.js - meta.attribute-with-value',
        'disable_if_not_dependency': True
    }

class XOFixOnSave(sublime_plugin.EventListener):
    def on_post_save(self, view):
        if not SettingManager.get_setting('autofix_on_save'): return
        filePath = view.file_name()
        if(filePath):
            cmd = [CMD_XO, '--fix', filePath]
            startupinfo=None
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

class XoFixFile(sublime_plugin.TextCommand):
   def run(self, edit):
        self.view.run_command('save')
        filePath = self.view.file_name()
        if(filePath):
            cmd = [CMD_XO, '--fix', filePath]
            startupinfo=None
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
