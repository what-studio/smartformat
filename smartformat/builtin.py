# -*- coding: utf-8 -*-
"""
   smartformat.builtin
   ~~~~~~~~~~~~~~~~~~~

   Built-in extensions from SmartFormat.NET, the original implementation.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import decimal
import io

from babel import Locale
from six import string_types

from .smart import default_extensions, extension
from .utils import get_plural_tag_index


__all__ = ['choose', 'conditional', 'list_', 'plural']


@extension(['plural', 'p', ''])
def plural(formatter, value, name, option, format):
    """Chooses different textension for locale-specific pluralization rules.

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
    except (ValueError, decimal.InvalidOperation):
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


@extension(['choose', 'c'])
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


@extension(['conditional', 'cond'])
def conditional(formatter, value, name, option, format):
    """SmartFormat for Python doesn't implement it because SmartFormat.NET has
    deprecated the 'conditional' extension.
    """
    raise NotImplementedError('Obsolete extension: conditional')


@extension(['list', 'l', ''])
def list_(formatter, value, name, option, format):
    """Repeats the items of an array.

    Spec: `{:[l[ist]:]item|spacer[|final_spacer[|two_spacer]]}`

    Example::

       >>> fruits = [u'apple', u'banana', u'coconut']
       >>> smart.format(u'{fruits:list:{}|, |, and | and }', fruits=fruits)
       u'apple, banana, and coconut'
       >>> smart.format(u'{fruits:list:{}|, |, and | and }', fruits=fruits[:2])
       u'apple and banana'

    """
    if not format:
        return
    if not hasattr(value, '__getitem__') or isinstance(value, string_types):
        return
    words = format.split(u'|', 4)
    num_words = len(words)
    if num_words < 2:
        # Require at least two words for item format and spacer.
        return
    num_items = len(value)
    item_format = words[0]
    # NOTE: SmartFormat.NET treats a not nested item format as the format
    # string to format each items.  For example, `x` will be treated as `{:x}`.
    # But the original tells us this behavior has been deprecated so that
    # should be removed.  So SmartFormat for Python doesn't implement the
    # behavior.
    spacer = u'' if num_words < 2 else words[1]
    final_spacer = spacer if num_words < 3 else words[2]
    two_spacer = final_spacer if num_words < 4 else words[3]
    buf = io.StringIO()
    for x, item in enumerate(value):
        if x == 0:
            pass
        elif x < num_items - 1:
            buf.write(spacer)
        elif x == 1:
            buf.write(two_spacer)
        else:
            buf.write(final_spacer)
        buf.write(formatter.format(item_format, item, index=x))
    return buf.getvalue()


# Register to the default extensions registry.
default_extensions.extend([plural, choose, conditional, list_])
