# -*- coding: utf-8 -*-
"""
   smartformat.dotnet
   ~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import string

from babel import Locale
from babel.numbers import (
    format_currency, get_territory_currencies, LC_NUMERIC, NumberPattern)
from valuedispatch import valuedispatch


NUMBER_DECIMAL_DIGITS = 2
PERCENT_DECIMAL_DIGITS = 2


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
    return str(value)


@format_field.register(u'c')
def format_currency_field(__, prec, number, locale):
    """Formats a currency field."""
    locale = Locale.parse(locale)
    currency = get_territory_currencies(locale.territory)[0]
    if prec is None:
        pattern, currency_digits = None, True
    else:
        pattern = locale.currency_formats['standard']
        pattern = modify_number_pattern(pattern, frac_prec=(prec, prec))
        currency_digits = False
    return format_currency(number, currency, pattern, locale=locale,
                           currency_digits=currency_digits)


@format_field.register(u'n')
def format_number_field(__, prec, number, locale):
    """Formats a number field."""
    if prec is None:
        prec = NUMBER_DECIMAL_DIGITS
    locale = Locale.parse(locale)
    pattern = locale.decimal_formats.get(None)
    return pattern.apply(number, locale, force_frac=(prec, prec))


@format_field.register(u'p')
def format_percent_field(__, prec, number, locale):
    """Formats a percent field."""
    if prec is None:
        prec = PERCENT_DECIMAL_DIGITS
    locale = Locale.parse(locale)
    # Percent formats in Babel usually end with '\xa0%' in several languages.
    # But the .NET implementation doesn't insert '\xa0' before '%'.
    pattern = locale.percent_formats.get(None)
    pos_suffix, neg_suffix = pattern.suffix
    suffix = (pos_suffix.lstrip(), neg_suffix.lstrip())
    pattern = modify_number_pattern(pattern, suffix=suffix)
    return pattern.apply(number, locale, force_frac=(prec, prec))


@format_field.register(u'd')
@format_field.register(u'e')
@format_field.register(u'f')
@format_field.register(u'g')
@format_field.register(u'r')
@format_field.register(u'x')
def format_not_implemented_field(spec, *args, **kwargs):
    raise NotImplementedError('Numeric format specifier %r '
                              'is not implemented yet' % spec)


class DotNetFormatter(string.Formatter):
    """A string formatter like `String.Format` in .NET Framework."""

    _format_field = staticmethod(format_field)

    def __init__(self, locale=None):
        self.locale = locale

    @property
    def numeric_locale(self):
        return self.locale or LC_NUMERIC

    def get_value(self, key, args, kwargs):
        if isinstance(key, str):
            key, comma, width = key.partition(',')
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
            spec = spec.lower()
            arg = int(arg) if arg else None
        else:
            spec = arg = None
        return self._format_field(spec, arg, value, self.numeric_locale)
