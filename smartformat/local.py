# -*- coding: utf-8 -*-
"""
   smartformat.local
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import decimal
import re
import string

from babel import Locale
from babel.numbers import LC_NUMERIC, NumberPattern


__all__ = ['LocalFormatter']


FORMAT_SPEC_PATTERN = re.compile(r'''
    ^
    (?:
        (?P<fill> .+)?
        (?P<align> [<>=^])
    )?
    (?P<sign> [+\-\ ])?
    (?P<sharp> \#)?
    (?P<zero> 0)?
    (?P<width> [0-9]+)?
    (?P<comma> ,)?
    (?:
        \.
        (?P<prec> [0-9]+)
    )?
    (?P<type> [bcdeEfFgGnosxX%])?
    $
''', re.VERBOSE)


def modify_number_pattern(number_pattern, **kwargs):
    """Modifies a number pattern by specified keyword arguments."""
    params = ['pattern', 'prefix', 'suffix', 'grouping',
              'int_prec', 'frac_prec', 'exp_prec', 'exp_plus']
    for param in params:
        if param in kwargs:
            continue
        kwargs[param] = getattr(number_pattern, param)
    return NumberPattern(**kwargs)


def format_number(value, prec=0, prefix=None, locale=LC_NUMERIC):
    locale = Locale.parse(locale)
    pattern = locale.decimal_formats.get(None)
    prefix = prefix or pattern.prefix
    return pattern.apply(value, locale, force_frac=(prec, prec))


def format_percent(value, prec=0, prefix=None, locale=LC_NUMERIC):
    locale = Locale.parse(locale)
    pattern = locale.percent_formats.get(None)
    prefix = prefix or pattern.prefix
    pos_suffix, neg_suffix = pattern.suffix
    suffix = (pos_suffix.lstrip(), neg_suffix.lstrip())
    pattern = modify_number_pattern(pattern, prefix=prefix, suffix=suffix)
    return pattern.apply(value, locale, force_frac=(prec, prec))


class LocalFormatter(string.Formatter):
    """A formatter which keeps a locale."""

    def __init__(self, locale):
        self.locale = Locale.parse(locale)

    @property
    def numeric_locale(self):
        return self.locale or LC_NUMERIC

    def format_field(self, value, format_spec):
        match = FORMAT_SPEC_PATTERN.match(format_spec)
        if match is not None:
            rv = self.format_field_by_match(value, match)
            if rv is not None:
                return rv
        base = super(LocalFormatter, self)
        return base.format_field(value, format_spec)

    def format_field_by_match(self, value, match):
        groups = match.groups()
        fill, align, sign, sharp, zero, width, comma, prec, type_ = groups
        if not comma:
            return None
        locale = self.numeric_locale
        if not sign or sign == u'-':
            prefix = (u'', u'-')
        else:
            prefix = (sign, u'-')
        if type_ == 'd':
            if prec is not None:
                raise ValueError('Precision not allowed in '
                                 'integer format specifier')
            string = format_number(value, 0, prefix, locale)
        elif type_ in 'fF':
            try:
                string = format_number(value, int(prec or 0), prefix, locale)
            except decimal.InvalidOperation:
                return None
        elif type_ == '%':
            try:
                string = format_percent(value, int(prec or 0), prefix, locale)
            except decimal.InvalidOperation:
                return None
        else:
            return None
        spec = ''.join([fill or u'', align or u'',
                        zero or u'', width or u''])
        return format(string, spec)


# f = LocalFormatter('hi_IN')
# print(f.format(u'{0:^020,.5f}', 123456789.123456789))
# print(str.format(u'{0:^020,.5f}', 123456789.123456789))
# print(f.format(u'{0:^+020,.5f}', 123456789.123456789))
# print(str.format(u'{0:^+020,.5f}', 123456789.123456789))
# print(f.format(u'{0:^010,.5f}', float('inf')))
# print(str.format(u'{0:^010,.5f}', float('inf')))
# print(f.format(u'{0:.10%}', 123456))
# print(f.format(u'{0:,.10%}', 123456))
