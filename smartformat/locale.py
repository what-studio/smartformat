# -*- coding: utf-8 -*-
"""
   smartformat.locale
   ~~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import string

from babel import default_locale, Locale
from babel.numbers import LC_NUMERIC


__all__ = ['LocaleFormatter']


class LocaleFormatter(string.Formatter):
    """A formatter which keeps a locale.  It doesn't anything else."""

    def __init__(self, locale=None):
        if locale is None:
            locale = default_locale()
        self.locale = Locale.parse(locale)

    @property
    def numeric_locale(self):
        return self.locale or LC_NUMERIC
