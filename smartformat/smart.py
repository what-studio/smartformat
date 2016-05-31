# -*- coding: utf-8 -*-
"""
   smartformat.smart
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from collections import deque
import re
import string

from .dotnet import DotNetFormatter
from .locale import LocaleFormatter


__all__ = ['default_extensions', 'extension', 'SmartFormatter',
           'SmartFormatterMixin']


#: The extensions to be registered by default.
default_extensions = deque()


NAME_PATTERN = re.compile(r'[a-zA-Z_]*')
SMART_FORMAT_SPEC_PATTERN = re.compile(r'''
    (?:
        (?P<name>[a-zA-Z_]+)
        (?:
            \((?P<option>.*)\)
        )?
        :
    )?
    (?P<format>.*)
''', re.VERBOSE | re.UNICODE)


# :meth:`string.Formatter._vformat` on Python 3.5.1 returns a pair
# `(format_spec, auto_arg_index)`.  The method is not public but we should
# override it to keep nested format specs.
f = string.Formatter()
VFORMAT_RETURNS_TUPLE = isinstance(f._vformat('', (), {}, [], 0), tuple)
del f


def parse_smart_format_spec(format_spec):
    m = SMART_FORMAT_SPEC_PATTERN.match(format_spec)
    return m.group('name') or u'', m.group('option'), m.group('format')


class SmartFormatterMixin(LocaleFormatter):
    """The mixin class which implements SmartFormat specifications.  Extend
    this with another formatter to deal with non-SmartFormat specifications.
    """

    def __init__(self, locale=None, extensions=(), register_default=True):
        super(SmartFormatterMixin, self).__init__(locale)
        # Currently implemented only formatter extensions.
        self._extensions = {}
        if register_default:
            self.register(default_extensions)
        self.register(extensions)

    def register(self, extensions):
        """Registers extensions."""
        for ext in reversed(extensions):
            for name in ext.names:
                try:
                    self._extensions[name].appendleft(ext)
                except KeyError:
                    self._extensions[name] = deque([ext])

    def format_field(self, value, format_spec):
        name, option, format = parse_smart_format_spec(format_spec)
        rv = self.eval_extensions(value, name, option, format)
        if rv is not None:
            return rv
        base = super(SmartFormatterMixin, self)
        return base.format_field(value, format_spec)

    def eval_extensions(self, value, name, option, format):
        """Evaluates extensions in the registry.  If some extension handles the
        format string, it returns a string.  Otherwise, returns ``None``.
        """
        for ext in self._extensions.get(name, ()):
            rv = ext(self, value, name, option, format)
            if rv is not None:
                return rv

    def get_value(self, field_name, args, kwargs):
        if not field_name:
            # `{}` is same with `{0}`.
            field_name = 0
        base = super(SmartFormatterMixin, self)
        return base.get_value(field_name, args, kwargs)

    def _vformat(self, format_string, _1, _2, _3,
                 recursion_depth, *args, **kwargs):
        if recursion_depth != 2:
            # Don't format recursive format strings such as `{:12{this}34}`.
            if VFORMAT_RETURNS_TUPLE:
                return (format_string, False)
            else:
                return format_string
        base = super(SmartFormatterMixin, self)
        return base._vformat(format_string, _1, _2, _3, 1, *args, **kwargs)


class SmartFormatter(SmartFormatterMixin, DotNetFormatter):
    """The official SmartFormat formatter.  To imitate SmartFormat.NET, this
    extends :class:`DotNetFormatter`.  So you can use .NET format
    specifications also::

       >>> smart = SmartFormatter('hi_IN')
       >>> print(smart.format(u'{:an item|{:n0} items}', 123456789))
       12,34,56,789 items

    If you don't want to use .NET format specifications, define your own
    SmartFormat formatter.  For example, you would choose
    :class:`NumberFormatter` to format localized numbers::

       class MySmartFormatter(SmartFormatterMixin, NumberFormatter):

           pass

       >>> my_smart = MySmartFormatter('hi_IN')
       >>> print(my_smart.format(u'{:an item|{:,d} items}', 123456789))
       12,34,56,789 items

    """

    pass


class Extension(object):
    """A formatter extension which wraps a function.  It works like a wrapped
    function but has several specific attributes and methods.

    A funciton to be an extension takes `(name, option, format)`.  The funcion
    should return a string as the result or ``None`` to pass to format a
    string.

    To make an extension, use `@extension` decorator.

    """

    def __init__(self, function, names):
        self.function = function
        self.names = names

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def extension(names):
    """Makes a function to be an extension."""
    for name in names:
        if not NAME_PATTERN.match(name):
            raise ValueError('Invalid extension name: %s' % name)
    def decorator(f, names=names):
        return Extension(f, names=names)
    return decorator


# Register built-in extensions.
from . import builtin  # noqa
del builtin
