# -*- coding: utf-8 -*-
"""
   smartformat.number
   ~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import math
from numbers import Number
import re

from babel import Locale
from babel.numbers import (
    get_group_symbol, get_minus_sign_symbol, get_plus_sign_symbol, LC_NUMERIC,
    NumberPattern)
from six import integer_types

from .locale import LocaleFormatter


__all__ = ['NumberFormatter']


DEFAULT_PREC = 6
NUMBER_FORMAT_SPEC_PATTERN = re.compile(r'''
    ^
    (?:
        (?P<fill> .+)?
        (?P<align> [<>=^])
    )?
    (?P<sign> [+\-\ ])?
    (?P<sharp> \#)?  # ignored.
    (?P<zero> 0)?
    (?P<width> [0-9]+)?
    (?P<comma> ,)?
    (?:
        \.
        (?P<prec> [0-9]+)
    )?
    (?P<type> [dfF%])?
    $
''', re.VERBOSE)
LAST_DIGIT_PATTERN = re.compile(r'[^0-9]*$')


def modify_number_pattern(number_pattern, **kwargs):
    """Modifies a number pattern by specified keyword arguments."""
    params = ['pattern', 'prefix', 'suffix', 'grouping',
              'int_prec', 'frac_prec', 'exp_prec', 'exp_plus']
    for param in params:
        if param in kwargs:
            continue
        kwargs[param] = getattr(number_pattern, param)
    return NumberPattern(**kwargs)


def format_number(number, prec=0, prefix=None, locale=LC_NUMERIC):
    locale = Locale.parse(locale)
    pattern = locale.decimal_formats.get(None)
    if prefix is not None:
        pattern = modify_number_pattern(pattern, prefix=prefix)
    return pattern.apply(number, locale, force_frac=(prec, prec))


def format_percent(number, prec=0, prefix=None, strip_suffix=False,
                   locale=LC_NUMERIC):
    locale = Locale.parse(locale)
    pattern = locale.percent_formats.get(None)
    if prefix is not None:
        pattern = modify_number_pattern(pattern, prefix=prefix)
    if strip_suffix:
        pos_suffix, neg_suffix = pattern.suffix
        suffix = (pos_suffix.lstrip(), neg_suffix.lstrip())
        pattern = modify_number_pattern(pattern, suffix=suffix)
    return pattern.apply(number, locale, force_frac=(prec, prec))


def remove_group_symbols(string, locale=LC_NUMERIC):
    symbol = get_group_symbol(locale)
    if string[-1].isdigit():
        return string.replace(symbol, u'')
    m = LAST_DIGIT_PATTERN.search(string)
    x = m.start()
    return string[:x].replace(symbol, u'') + string[x:]


def sign_to_prefix(sign, locale=LC_NUMERIC):
    if sign == u'-':
        plus_symbol = u''
    elif sign == u' ':
        plus_symbol = u' '
    else:  # sign == '+'
        plus_symbol = get_plus_sign_symbol(locale)
    minus_symbol = get_minus_sign_symbol(locale)
    return (plus_symbol, minus_symbol)


class NumberFormatter(LocaleFormatter):
    """Formats localized numbers by the standard number format types:
    'd', 'f', 'F', '%'.
    """

    def format_field(self, value, format_spec):
        if isinstance(value, Number) and math.isfinite(value):
            match = NUMBER_FORMAT_SPEC_PATTERN.match(format_spec)
            if match is not None:
                rv = self.format_number_field_by_match(value, match)
                if rv is not None:
                    return rv
        base = super(NumberFormatter, self)
        return base.format_field(value, format_spec)

    def format_number_field_by_match(self, value, match):
        """Formats a nubmer field by a Regex match of the format spec pattern.
        """
        groups = match.groups()
        fill, align, sign, __, zero, width, comma, prec, type_ = groups
        # Set defaults.
        fill = fill or u''
        align = align or u'>'
        sign = sign or u'-'
        zero = zero or u''
        width = width or u''
        if type_ is None:
            if not isinstance(value, integer_types):
                return None
            type_ = u'd'
        return self.format_number_field(value, fill, align, sign, zero, width,
                                        comma, prec, type_)

    def format_number_field(self, value, fill, align, sign, zero, width, comma,
                            prec, type_):
        """Formats a number field by the format spec."""
        locale = self.numeric_locale
        # Determine prefix.
        pad_after_prefix = align == u'='
        pos_prefix, neg_prefix = sign_to_prefix(sign, locale)
        prefix = (u'', u'') if pad_after_prefix else (pos_prefix, neg_prefix)
        # Determine precision.
        if type_ == u'd':
            if prec is not None:
                raise ValueError('Precision not allowed in integer format '
                                 'specifier')
            if not isinstance(value, integer_types):
                raise ValueError("Unknown format code 'd' for object of type "
                                 "'%s'" % value.__class__.__name__)
            prec = 0
        else:
            prec = int(prec or DEFAULT_PREC)
        # Format number value.
        format_value = format_percent if type_ == u'%' else format_number
        string = format_value(value, prec, prefix, locale=locale)
        if not comma:
            # Formatted number always contains group symbols.  Remove the
            # symbols if not required.
            string = remove_group_symbols(string, locale)
        if not (fill or (not pad_after_prefix and align) or zero or width):
            # No layout spec.
            return string
        # Fix a layout.
        if pad_after_prefix:
            align = u'>'
            length_without_layout = len(string)
        spec = u''.join([fill, align, zero, width])
        string = format(string, spec)
        # Insert sign if align is '='.
        if pad_after_prefix:
            length_diff = len(string) - length_without_layout
            prefix = neg_prefix if value < 0 else pos_prefix
            if prefix:
                string = prefix + string[min(length_diff, len(prefix)):]
        return string
