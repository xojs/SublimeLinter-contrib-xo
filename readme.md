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

Also you can change general plugin setting from:

`Preferences > Package Settings > SublimeLinter XO`

## Auto-fix

To run the auto-fixer, press the `ctrl+alt+f` shortcut (can be changed) or use the menu entry “Tools › SublimeLinter XO › Fix current file”.

If you want to run the auto-fixer when saving a file, you can enable the `fix_on_save` setting:

```json
{
	"fix_on_save": true
}
```

## Tips

### Using non-JS syntax

Typical plugins for ESLint, for example, for TypeScript or Vue, should just work automatically if they're installed locally in your project (defined in the same `package.json`).

For plugins not supported out-of-the-box, you may need to change the SublimeLinter [`selector` setting](http://www.sublimelinter.com/en/stable/linter_settings.html#selector) to include the correct syntax scope. For Vue, that could be:

```json
{
	"linters": {
		"xo": {
			"selector": "text.html.vue, source.js - meta.attribute-with-value"
		}
	}
}
```

### Help, `xo` doesn't lint my HTML files anymore!

`xo` will only lint `*.js` files for standard, vanilla config without further plugins. Either install the [eslint-plugin-html](https://github.com/BenoitZugmeyer/eslint-plugin-html) or tweak the `selector`:

```json
{
	"linters": {
		"xo": {
			"selector": "source.js - meta.attribute-with-value"
		}
	}
}
```

## Note

XO linting is only enabled for projects with `xo` in `devDependencies`/`dependencies` in package.json.
