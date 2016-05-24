# -*- coding: utf-8 -*-
"""
   smartformat.extensions
   ~~~~~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import decimal

from .smart import ext
from .utils import get_plural_tag_index


__all__ = ['plural']


@ext(['plural', 'p', ''], pass_formatter=True)
def plural(formatter, value, name, opts, format):
    # Extract the plural words from the format string.
    words = format.split('|')
    # This extension requires at least two plural words.
    if len(words) == 1:
        return
    # This extension only formats numbers.
    try:
        number = decimal.Decimal(value)
    except decimal.InvalidOperation:
        return
    # Select word based on the plural tag index.
    index = get_plural_tag_index(number, formatter.locale)
    return formatter.format(words[index], value)


@ext(['choose', 'c'])
def choose(value, name, opts, format):
    pass


#: The list of default extensions.
DEFAULT_EXTENSIONS = [plural]
