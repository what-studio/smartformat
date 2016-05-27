# SmartFormat for Python

[![Build Status]
(https://img.shields.io/travis/what-studio/smartformat.svg)]
(https://travis-ci.org/what-studio/smartformat)
[![Coverage Status]
(https://img.shields.io/coveralls/what-studio/smartformat.svg)]
(https://coveralls.io/r/what-studio/smartformat)

[SmartFormat] is a powerful string formatter which was introduced on the .NET
community.  Especially the formatter is helpful for making an
internationalization system.  You can make a text template for multiple
pluralizable words for the whole of the natural languages.

This library provides a Python string formatter which imitates
[SmartFormat.NET] based on `string.Formatter` in the standard library and
[Babel] for internationalization.

Currently, this library doesn't implement the full specification yet.  Because
the localization models in Babel and .NET have some differences with each
other.

[SmartFormat]: https://github.com/scottrippey/SmartFormat
[SmartFormat.NET]: https://github.com/scottrippey/SmartFormat.NET
[Babel]: http://babel.pocoo.org/

## Usage

Install via PyPI first:

```console
$ pip install smartformat
```

Then use like a `string.Formatter`:

```python
>>> from smartformat import SmartFormatter
>>> smart = SmartFormatter('en_US')
>>> text = u'{gender:c(male|female):He|She} got {num_items:an item|{} items}.'
>>> smart.format(text, gender=Gender.male, num_items=1)
He got an item.
>>> smart.format(text, gender=Gender.female, num_items=42)
She got 42 items.
```

## .NET `String.Format` Specs

- [x] `{:n}` - Number
- [x] `{:n3}` - Number with specific fractional precision
- [x] `{:p}` - Percent
- [x] `{:p3}` - Percent with specific fractional precision
- [x] `{:c}` - Currency (JPY symbol is different with .NET)
- [x] `{:c3}` - Currency with specific fractional precision
- [ ] `{:-c}` - Negative currency
- [ ] `{:d}`
- [ ] `{:e}`
- [ ] `{:f}`
- [ ] `{:g}`
- [ ] `{:r}`
- [ ] `{:x}`

## SmartFormat Specs

- [ ] Nested Placeholder
- [ ] Getting value by attribute
- [x] Plural Extension: `{:an item|{} items}`
- [x] Choose Extension: `{:choose(male|female):He|She}`
- [ ] Conditional Extension - Originally deprecated, we won't implement it.
- [x] List Extension: `{:{}|, |, and }`
- [ ] Time Extension

## Custom Extension

To make your own extension, define a function which takes `(formatter, value,
name, option, format)` parameters and decorate with `@smartformat.extension`:

```python
import smartformat

@smartformat.extension(['hello'])
def hello(formatter, value, name, option, format):
    return 'HELLO ' + (option if value else format)
```

Register any extension to a `SmartFormatter` instance:

```python
>>> smart = SmartFormatter('en_US', [hello])
>>> smart.format(u'{:hello(world):earth}', True)
HELLO world
>>> smart.format(u'{:hello(world):earth}', False)
HELLO earth
```

An extension can be dispatched without name implicitly.  If you want to do so,
set `''` as a one of the extension names.  Implicit extension may skip to
format some inputs by returning `None`:

```python
@smartformat.extension(['foo', ''])
def foo(formatter, value, name, option, format):
    if value:
        return 'foo'
    else:
        return
@smartformat.extension(['bar', ''])
def bar(formatter, value, name, option, format):
    return 'bar'
```

```python
>>> smart = SmartFormatter('en_US', [foo, bar])
>>> smart.format(u'{:}', True)
foo
>>> smart.format(u'{:}', False)
bar
```

The name of a module for SmartFormat extensions should starts with
`smartformat_`.  They can be imported under `smartformat.ext`.  For example,
`import smartformat.ext.hello` will import the `smartformat_hello` module
actually.  Just like `flask.ext`!

## Licensing

Written or designed by [Heungsub Lee] at [What! Studio] in [Nexon],
and distributed under the [BSD 3-Clause] license.

[Heungsub Lee]: http://subl.ee/
[What! Studio]: https://github.com/what-studio
[Nexon]: http://nexon.com/
[BSD 3-Clause]: http://opensource.org/licenses/BSD-3-Clause
