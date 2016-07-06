# -*- coding: utf-8 -*-
"""
   smartformat.dotnet
   ~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import math
from numbers import Number

from babel import Locale
from babel.numbers import (
    format_currency, get_decimal_symbol, get_territory_currencies,
    NumberPattern, parse_pattern)
from six import string_types, text_type as str
from valuedispatch import valuedispatch

from .local import LocalFormatter


__all__ = ['DotNetFormatter']


NUMBER_DECIMAL_DIGITS = 2
PERCENT_DECIMAL_DIGITS = 2
SCIENTIFIC_DECIMAL_DIGITS = 6


def modify_number_pattern(number_pattern, **kwargs):
    """Modifies a number pattern by specified keyword arguments."""
    params = ['pattern', 'prefix', 'suffix', 'grouping',
              'int_prec', 'frac_prec', 'exp_prec', 'exp_plus']
    for param in params:
        if param in kwargs:
            continue
        kwargs[param] = getattr(number_pattern, param)
    return NumberPattern(**kwargs)


@valuedispatch
def format_field(spec, arg, value, locale):
    if spec and isinstance(value, Number):
        if arg:
            spec += arg
        pattern = parse_pattern(spec)
        return pattern.apply(value, locale)
    return str(value)


@format_field.register(u'c')
@format_field.register(u'C')
def format_currency_field(__, prec, number, locale):
    """Formats a currency field."""
    locale = Locale.parse(locale)
    currency = get_territory_currencies(locale.territory)[0]
    if prec is None:
        pattern, currency_digits = None, True
    else:
        prec = int(prec)
        pattern = locale.currency_formats['standard']
        pattern = modify_number_pattern(pattern, frac_prec=(prec, prec))
        currency_digits = False
    return format_currency(number, currency, pattern, locale=locale,
                           currency_digits=currency_digits)


@format_field.register(u'd')
@format_field.register(u'D')
def format_decimal_field(__, prec, number, locale):
    """Formats a decimal field:

    .. sourcecode::

       1234 ('D') -> 1234
       -1234 ('D6') -> -001234

    """
    prec = 0 if prec is None else int(prec)
    if number < 0:
        prec += 1
    return format(number, u'0%dd' % prec)


@format_field.register(u'e')
@format_field.register(u'E')
def format_scientific_field(spec, prec, number, locale):
    prec = SCIENTIFIC_DECIMAL_DIGITS if prec is None else int(prec)
    format_ = u'0.%sE+000' % (u'#' * prec)
    pattern = parse_pattern(format_)
    decimal_symbol = get_decimal_symbol(locale)
    string = pattern.apply(number, locale).replace(u'.', decimal_symbol)
    return string.lower() if spec.islower() else string


@format_field.register(u'f')
@format_field.register(u'F')
def format_float_field(__, prec, number, locale):
    """Formats a fixed-point field."""
    format_ = u'0.'
    if prec is None:
        format_ += u'#' * NUMBER_DECIMAL_DIGITS
    else:
        format_ += u'0' * int(prec)
    pattern = parse_pattern(format_)
    return pattern.apply(number, locale)


@format_field.register(u'n')
@format_field.register(u'N')
def format_number_field(__, prec, number, locale):
    """Formats a number field."""
    prec = NUMBER_DECIMAL_DIGITS if prec is None else int(prec)
    locale = Locale.parse(locale)
    pattern = locale.decimal_formats.get(None)
    return pattern.apply(number, locale, force_frac=(prec, prec))


@format_field.register(u'p')
@format_field.register(u'P')
def format_percent_field(__, prec, number, locale):
    """Formats a percent field."""
    prec = PERCENT_DECIMAL_DIGITS if prec is None else int(prec)
    locale = Locale.parse(locale)
    # Percent formats in Babel usually end with '\xa0%' in several languages.
    # But the .NET implementation doesn't insert '\xa0' before '%'.
    pattern = locale.percent_formats.get(None)
    pos_suffix, neg_suffix = pattern.suffix
    suffix = (pos_suffix.lstrip(), neg_suffix.lstrip())
    pattern = modify_number_pattern(pattern, suffix=suffix)
    return pattern.apply(number, locale, force_frac=(prec, prec))


@format_field.register(u'x')
@format_field.register(u'X')
def format_hexadecimal_field(spec, prec, number, locale):
    """Formats a hexadeciaml field."""
    if number < 0:
        # Take two's complement.
        number &= (1 << (8 * int(math.log(-number, 1 << 8) + 1))) - 1
    format_ = u'0%d%s' % (int(prec or 0), spec)
    return format(number, format_)


@format_field.register(u'g')
@format_field.register(u'G')
@format_field.register(u'r')
@format_field.register(u'R')
def format_not_implemented_field(spec, *args, **kwargs):
    raise NotImplementedError('Numeric format specifier %r '
                              'is not implemented yet' % spec)


class DotNetFormatter(LocalFormatter):
    """A string formatter like `String.Format` in .NET Framework."""

    _format_field = staticmethod(format_field)

    def vformat(self, format_string, args, kwargs):
        if not format_string:
            return u''
        base = super(DotNetFormatter, self)
        return base.vformat(format_string, args, kwargs)

    def get_value(self, key, args, kwargs):
        if isinstance(key, string_types):
            key, comma, width = key.partition(u',')
            if comma:
                raise NotImplementedError('Width specifier after comma '
                                          'is not implemented yet')
        return super(DotNetFormatter, self).get_value(key, args, kwargs)

    def format_field(self, value, format_spec):
        """Format specifiers are described in :func:`format_field` which is a
        static function.
        """
        if format_spec:
            spec, arg = format_spec[0], format_spec[1:]
            arg = arg or None
        else:
            spec = arg = None
        return self._format_field(spec, arg, value, self.numeric_locale)
