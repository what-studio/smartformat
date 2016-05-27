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


__all__ = ['default_extensions', 'extension', 'SmartFormatter']


#: The extensions to be registered by default.
default_extensions = deque()


NAME_PATTERN = re.compile(r'[a-zA-Z_]*')
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

    def __init__(self, locale=None, extensions=(), register_default=True):
        super(SmartFormatter, self).__init__(locale)
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
            rv = ext(self, value, name, option, format)
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
