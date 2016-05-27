# -*- coding: utf-8 -*-
"""
   smartformat.ext
   ~~~~~~~~~~~~~~~

   Redirects imports for extensions.  Stolen from `flask.ext`.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""


def setup():
    from ..exthook import ExtensionImporter
    importer = ExtensionImporter(['smartformat_%s'], __name__)
    importer.install()


setup()
del setup
