# -*- coding: utf-8 -*-
"""
   smartformat.extensions
   ~~~~~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import decimal

from babel import Locale

from .smart import ext
from .utils import get_plural_tag_index


__all__ = ['plural']


@ext(['plural', 'p', ''], pass_formatter=True)
def plural(formatter, value, name, opts, format):
    # Extract the plural words from the format string.
    words = format.split('|')
    # This extension requires at least two plural words.
    if not name and len(words) == 1:
        return
    # This extension only formats numbers.
    try:
        number = decimal.Decimal(value)
    except decimal.InvalidOperation:
        return
    # Get the locale.
    locale = Locale.parse(opts) if opts else formatter.locale
    # Select word based on the plural tag index.
    index = get_plural_tag_index(number, locale)
    return formatter.format(words[index], value)


def get_choice(value):
    """Gets a key to choose a choice from any value."""
    if value is None:
        return 'null'
    for attr in ['__name__', 'name']:
        if hasattr(value, attr):
            return getattr(value, attr)
    return str(value)


@ext(['choose', 'c'], pass_formatter=True)
def choose(formatter, value, name, opts, format):
    if not opts:
        return
    words = format.split('|')
    if len(words) < 2:
        return
    choices = opts.split('|')
    choice = get_choice(value)
    try:
        index = choices.index(choice)
    except ValueError:
        index = -1
    return formatter.format(words[index], value)


#: The list of default extensions.
DEFAULT_EXTENSIONS = [plural, choose]
