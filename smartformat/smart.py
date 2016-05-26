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


__all__ = ['ext', 'SmartFormatter']


FORMAT_SPEC_PATTERN = re.compile(r'''
    (?:
        (?P<name>[a-zA-Z_]+)
        (?:
            \((?P<option>.*)\)
        )?
        :
    )?
    (?P<format>.*)
''', re.VERBOSE | re.UNICODE)


def parse_format_spec(format_spec):
    m = FORMAT_SPEC_PATTERN.match(format_spec)
    return m.group('name') or u'', m.group('option'), m.group('format')


class SmartFormatter(DotNetFormatter):

    def __init__(self, locale=None, register_builtin=True):
        super(SmartFormatter, self).__init__(locale)
        # Currently implemented only formatter extensions.
        self._extensions = {}
        if register_builtin:
            from .builtin import BUILTIN_EXTENSIONS
            self.register(BUILTIN_EXTENSIONS)

    def register(self, extensions):
        """Registers extensions."""
        for ext in extensions[::-1]:
            for name in ext.names:
                try:
                    self._extensions[name].appendleft(ext)
                except KeyError:
                    self._extensions[name] = deque([ext])

    def format_field(self, value, format_spec):
        name, option, format = parse_format_spec(format_spec)
        rv = self.eval_extensions(value, name, option, format)
        if rv is not None:
            return rv
        return super(SmartFormatter, self).format_field(value, format_spec)

    def eval_extensions(self, value, name, option, format):
        """Evaluates extensions in the registry.  If some extension handles the
        format string, it returns a string.  Otherwise, returns ``None``.
        """
        for ext in self._extensions.get(name, ()):
            rv = ext.eval(self, value, name, option, format)
            if rv is not None:
                return rv

    def get_value(self, field_name, args, kwargs):
        if not field_name:
            # `{}` is same with `{0}`.
            field_name = 0
        return super(SmartFormatter, self).get_value(field_name, args, kwargs)

    def _vformat(self, format_string, args, kwargs,
                 used_args, recursion_depth):
        if recursion_depth != 2:
            # Don't format recursive format string such as `{:12{this}34}`.
            return format_string
        base = super(SmartFormatter, self)
        return base._vformat(format_string, args, kwargs, used_args, 2)


class Extension(object):
    """A formatter extension which wraps a function.  It works like a wrapped
    function but has several specific attributes and methods.

    A funciton to be an extension takes `(name, option, format)`.  If you set
    `pass_formatter=True` a smart formatter object will be passed as the first
    argument.  The funcion should return a string as the result or ``None``
    to pass to format a string.

    To make an extension, use `@ext` decorator.

    """

    def __init__(self, function, names, pass_formatter=False):
        self.function = function
        self.names = names
        self.pass_formatter = pass_formatter

    def eval(self, formatter, value, name, option, format):
        args = [formatter] if self.pass_formatter else []
        args.extend([value, name, option, format])
        return self.function(*args)

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)


def ext(names, pass_formatter=False):
    """Makes a function to be an extension."""
    for name in names:
        if '(' in name:
            raise ValueError("Extension name can't include '('")
    def decorator(f, names=names, pass_formatter=pass_formatter):
        return Extension(f, names=names, pass_formatter=pass_formatter)
    return decorator
