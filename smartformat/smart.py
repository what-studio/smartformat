# -*- coding: utf-8 -*-
"""
   smartformat.smart
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from collections import deque
import re

from .dotnet import DotNetFormatter


FORMAT_SPEC_PATTERN = re.compile(r'''
    (?:
        (?P<name>.+)
        (?:
            \((?P<opts>.*)\)
        )?
        :
    )?
    (?P<format>.*)
''', re.VERBOSE)


def parse_format_spec(format_spec):
    m = FORMAT_SPEC_PATTERN.match(format_spec)
    return m.group('name') or '', m.group('opts'), m.group('format')


class SmartFormatter(DotNetFormatter):

    def __init__(self, locale=None, register_default=True):
        super(SmartFormatter, self).__init__(locale)
        # Currently implemented only formatter extensions.
        self._extensions = {}
        if register_default:
            from .extensions import DEFAULT_EXTENSIONS
            self.register(DEFAULT_EXTENSIONS)

    def register(self, extensions):
        """Registers extensions."""
        for ext in extensions[::-1]:
            for name in ext.names:
                try:
                    self._extensions[name].appendleft(ext)
                except KeyError:
                    self._extensions[name] = deque([ext])

    def format_field(self, value, format_spec):
        name, opts, format = parse_format_spec(format_spec)
        rv = self.eval_formatter(value, name, opts, format)
        if rv is not None:
            return rv
        return super(SmartFormatter, self).format_field(value, format_spec)

    def eval_formatter(self, value, name, opts, format):
        for ext in self._extensions.get(name, ()):
            rv = ext.eval(self, value, name, opts, format)
            if rv is not None:
                return rv

    def get_value(self, field_name, args, kwargs):
        if not field_name:
            field_name = 0
        return super(SmartFormatter, self).get_value(field_name, args, kwargs)

    def _vformat(self, format_string, args, kwargs,
                 used_args, recursion_depth):
        if recursion_depth != 2:
            return format_string
        base = super(SmartFormatter, self)
        return base._vformat(format_string, args, kwargs, used_args, 2)


class Extension(object):
    """A formatter extension which wraps a function.  It works like a wrapped
    function but has several specific attributes and methods.

    A funciton to be an extension takes `(name, opts, format)`.  If you set
    `pass_formatter=True` a smart formatter object will be passed as the first
    argument.  The funcion should return a string as the result or ``None``
    to pass to format a string.

    To make an extension, use `@ext` decorator.

    """

    def __init__(self, function, names, pass_formatter=False):
        self.function = function
        self.names = names
        self.pass_formatter = pass_formatter

    def eval(self, formatter, value, name, opts, format):
        args = [formatter] if self.pass_formatter else []
        args.extend([value, name, opts, format])
        return self.function(*args)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def ext(names, pass_formatter=False):
    """Makes a function to be an extension."""
    def decorator(f, names=names, pass_formatter=pass_formatter):
        return Extension(f, names=names, pass_formatter=pass_formatter)
    return decorator
