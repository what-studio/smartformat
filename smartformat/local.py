# -*- coding: utf-8 -*-
"""
   smartformat.local
   ~~~~~~~~~~~~~~~~~

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import string

from babel import Locale
from babel.numbers import LC_NUMERIC


__all__ = ['LocalFormatter']


class LocalFormatter(string.Formatter):
    """A formatter which keeps a locale.  It doesn't anything else."""

    def __init__(self, locale):
        self.locale = Locale.parse(locale)

    @property
    def numeric_locale(self):
        return self.locale or LC_NUMERIC
