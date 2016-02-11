#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Sindre Sorhus
# Copyright (c) 2015 Sindre Sorhus
#
# License: MIT
#

"""This module exports the XO plugin class."""

from SublimeLinter.lint import NodeLinter


class XO(NodeLinter):
    """Provides an interface to XO."""

    cmd = 'xo --stdin --compact'
    regex = (
        r'^.+?: line (?P<line>\d+), col (?P<col>\d+), '
        r'(?:(?P<error>Error)|(?P<warning>Warning)) - '
        r'(?P<message>.+)'
    )
    selectors = {
        'html': 'source.js.embedded.html'
    }
    syntax = (
        'javascript',
        'html',
        'javascriptnext',
        'javascript (babel)',
        'javascript (jsx)',
        'jsx-real'
    )
    version_args = '--version'
    version_re = r'(?P<version>\d+\.\d+\.\d+)'
    version_requirement = '>=0.5.0'
