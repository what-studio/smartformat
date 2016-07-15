# -*- coding: utf-8 -*-
"""
   smartformat.smart
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from collections import deque
import io
import re
import string
import sys
from types import MethodType

from six import reraise, text_type

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


# :meth:`string.Formatter._vformat` on Python 3.5.1 returns a pair
# `(format_spec, auto_arg_index)`.  The method is not public but we should
# override it to keep nested format specs.
f = string.Formatter()
VFORMAT_RETURNS_TUPLE = isinstance(f._vformat('', (), {}, [], 0), tuple)
del f


def parse_format_spec(format_spec):
    m = FORMAT_SPEC_PATTERN.match(format_spec)
    return m.group('name') or u'', m.group('option'), m.group('format')


class SmartFormatter(DotNetFormatter):

    def __init__(self, locale=None, extensions=(), register_default=True,
                 errors='strict'):
        super(SmartFormatter, self).__init__(locale)
        # Set error action.
        try:
            _format_error = self._error_formatters[errors]
        except KeyError:
            raise LookupError('unknown error action name %s' % errors)
        self.format_error = MethodType(_format_error, self)
        if errors == 'skip':
            self.parse = self._parse_for_skip_error_action
        self.errors = errors
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
        try:
            rv = self.eval_extensions(value, name, option, format)
            if rv is not None:
                return rv
            base = super(SmartFormatter, self)
            return base.format_field(value, format_spec)
        except:
            return self.format_error(sys.exc_info())

    def eval_extensions(self, value, name, option, format):
        """Evaluates extensions in the registry.  If some extension handles the
        format string, it returns a string.  Otherwise, returns ``None``.
        """
        try:
            exts = self._extensions[name]
        except KeyError:
            raise ValueError('no suitable extension: %s' % name)
        for ext in exts:
            rv = ext(self, value, name, option, format)
            if rv is not None:
                return rv

    def get_value(self, field_name, args, kwargs):
        if not field_name:
            # `{}` is same with `{0}`.
            field_name = 0
        return super(SmartFormatter, self).get_value(field_name, args, kwargs)

    def _vformat(self, format_string, _1, _2, _3,
                 recursion_depth, *args, **kwargs):
        if recursion_depth != 2:
            # Don't format recursive format strings such as `{:12{this}34}`.
            if VFORMAT_RETURNS_TUPLE:
                return (format_string, False)
            else:
                return format_string
        base = super(SmartFormatter, self)
        return base._vformat(format_string, _1, _2, _3, 1, *args, **kwargs)

    def format_error(self, exc_info):
        raise NotImplementedError('will be set by __init__')

    def _format_error_for_strict_error_action(self, exc_info):
        reraise(*exc_info)

    def _format_error_for_errmsg_error_action(self, exc_info):
        __, exc, __ = exc_info
        return text_type(exc)

    def _format_error_for_ignore_error_action(self, exc_info):
        return u''

    def _format_error_for_skip_error_action(self, exc_info):
        __, field_name, format_spec, conversion = self._parsed
        buf = io.StringIO()
        buf.write(u'{%s' % field_name)
        if conversion:
            buf.write(u'!%s' % conversion)
        if format_spec:
            buf.write(u':%s' % format_spec)
        buf.write(u'}')
        return buf.getvalue()

    _error_formatters = {
        # ErrorAction.ThrowError in C# SmartFormat.
        'strict': _format_error_for_strict_error_action,
        # ErrorAction.OutputErrorInResult in C# SmartFormat.
        'errmsg': _format_error_for_errmsg_error_action,
        # ErrorAction.Ignore in C# SmartFormat.
        'ignore': _format_error_for_ignore_error_action,
        # ErrorAction.MaintainTokens in C# SmartFormat.
        'skip': _format_error_for_skip_error_action,
    }

    def _parse_for_skip_error_action(self, format_string):
        for parsed in super(SmartFormatter, self).parse(format_string):
            self._parsed = parsed
            yield parsed
            del self._parsed


ERROR_ACTIONS = list(SmartFormatter._error_formatters.keys())


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
            raise ValueError('invalid extension name: %s' % name)
    def decorator(f, names=names):
        return Extension(f, names=names)
    return decorator


# Register built-in extensions.
from . import builtin  # noqa
del builtin
