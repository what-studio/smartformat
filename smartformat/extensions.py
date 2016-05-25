# -*- coding: utf-8 -*-
"""
   smartformat.extensions
   ~~~~~~~~~~~~~~~~~~~~~~

   Default extensions from the original SmartFormat.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import decimal

from babel import Locale

from .smart import ext
from .utils import get_plural_tag_index


__all__ = ['plural']


@ext(['plural', 'p', ''], pass_formatter=True)
def plural(formatter, value, name, option, format):
    """Chooses different text for locale-specific pluralization rules.

    Spec: `{:[p[lural]][(locale)]:msgstr0|msgstr1|...}`

    Example::

       >>> smart.format(u'There {num:is an item|are {} items}.', num=1}
       There is an item.
       >>> smart.format(u'There {num:is an item|are {} items}.', num=10}
       There are 10 items.

    """
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
    locale = Locale.parse(option) if option else formatter.locale
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
def choose(formatter, value, name, option, format):
    """Adds simple logic to format strings.

    Spec: `{:c[hoose](choice1|choice2|...):word1|word2|...[|default]}`

    Example::

       >>> smart.format(u'{num:choose(1|2|3):one|two|three|other}, num=1)
       u'one'
       >>> smart.format(u'{num:choose(1|2|3):one|two|three|other}, num=4)
       u'other'

    """
    if not option:
        return
    words = format.split('|')
    num_words = len(words)
    if num_words < 2:
        return
    choices = option.split('|')
    num_choices = len(choices)
    # If the words has 1 more item than the choices, the last word will be
    # used as a default choice.
    if num_words not in (num_choices, num_choices + 1):
        n = num_choices
        raise ValueError('Specify %d or %d choices' % (n, n + 1))
    choice = get_choice(value)
    try:
        index = choices.index(choice)
    except ValueError:
        if num_words == num_choices:
            raise ValueError('No default choice supplied')
        index = -1
    return formatter.format(words[index], value)


@ext(['conditional', 'cond'])
def conditional(value, name, option, format):
    """SmartFormat for Python doesn't implement it because the original
    SmartFormatter has deprecated the 'conditional' extension.
    """
    raise NotImplementedError('Obsolete extension: conditional')


#: The list of default extensions.
DEFAULT_EXTENSIONS = [plural, choose, conditional]
