# SublimeLinter-contrib-xo

![](screenshot.png)

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) provides an interface to [XO](https://github.com/xojs/xo). It will be used with files that have the “JavaScript” syntax.


## Installation

SublimeLinter must be installed in order to use this plugin.

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

Before installing this plugin, you must ensure that `xo` is installed on your system:

```
$ npm install --global xo
```

In order for `xo` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. The docs cover [troubleshooting PATH configuration](https://sublimelinter.readthedocs.io/en/latest/troubleshooting.html#finding-a-linter-executable).


## Settings

- [SublimeLinter settings](https://sublimelinter.readthedocs.org/en/latest/settings.html)
- [Linter settings](https://sublimelinter.readthedocs.org/en/latest/linter_settings.html)


## Tips

### Using non-JS syntax

If you're using an ESLint plugin with XO that provides non-JS syntax, like TypeScript, Vue, etc, you need to change the SublimeLinter [`selector` setting](http://www.sublimelinter.com/en/stable/linter_settings.html#selector) to include the syntax scope. For Vue, that would be:

```json
{
	"linters": {
		"xo": {
			"selector": "text.html.vue, source.js - meta.attribute-with-value"
		}
	}
}
```


## Note

XO linting is only enabled for projects with `xo` in `devDependencies`/`dependencies` in package.json.


## License

MIT © [Sindre Sorhus](https://sindresorhus.com)
