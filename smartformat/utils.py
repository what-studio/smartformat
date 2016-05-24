# -*- coding: utf-8 -*-
"""
   smartformat.utils
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
from babel import Locale
from babel.plural import _fallback_tag, _plural_tags


__all__ = ['get_plural_tag_index']


def get_plural_tag_index(number, locale):
    """Gets the plural tag index of a number on the plural rule of a locale::

       >>> get_plural_tag_index(1, 'en_US')
       0
       >>> get_plural_tag_index(2, 'en_US')
       1
       >>> get_plural_tag_index(100, 'en_US')
       1

    """
    locale = Locale.parse(locale)
    plural_rule = locale.plural_form
    used_tags = plural_rule.tags | set([_fallback_tag])
    tag, index = plural_rule(number), 0
    for _tag in _plural_tags:
        if _tag == tag:
            return index
        if _tag in used_tags:
            index += 1
