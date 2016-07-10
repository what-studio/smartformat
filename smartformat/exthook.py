# -*- coding: utf-8 -*-
"""
   smartformat.exthook
   ~~~~~~~~~~~~~~~~~~~

   Implements an importer to redirect imports for extensions.  Stolen from
   `flask.exthook`.

   :copyright: (c) 2016 by What! Studio
   :license: BSD, see LICENSE for more details.

"""
import os
import sys

from six import reraise


class ExtensionImporter(object):
    """This importer redirects imports from this submodule to other locations.
    This makes it possible to transition from the old flaskext.name to the
    newer flask_name without people having a hard time.
    """

    def __init__(self, module_choices, wrapper_module):
        self.module_choices = module_choices
        self.wrapper_module = wrapper_module
        self.prefix = wrapper_module + '.'
        self.prefix_cutoff = wrapper_module.count('.') + 1

    # def __eq__(self, other):
    #     return (self.__class__.__module__ == other.__class__.__module__ and
    #             self.__class__.__name__ == other.__class__.__name__ and
    #             self.wrapper_module == other.wrapper_module and
    #             self.module_choices == other.module_choices)

    # def __ne__(self, other):
    #     return not self.__eq__(other)

    def install(self):
        sys.meta_path[:] = [x for x in sys.meta_path if self != x] + [self]

    def find_module(self, fullname, path=None):
        if fullname.startswith(self.prefix):
            return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        modname = fullname.split('.', self.prefix_cutoff)[self.prefix_cutoff]
        for path in self.module_choices:
            realname = path % modname
            try:
                __import__(realname)
            except ImportError:
                exc_type, exc_value, tb = sys.exc_info()
                sys.modules.pop(fullname, None)
                if self.is_important_traceback(realname, tb):
                    reraise(exc_type, exc_value, tb.tb_next)
                continue
            module = sys.modules[fullname] = sys.modules[realname]
            if '.' not in modname:
                setattr(sys.modules[self.wrapper_module], modname, module)
            return module
        raise ImportError('no module named %s' % fullname)

    def is_important_traceback(self, important_module, tb):
        while tb is not None:
            if self.is_important_frame(important_module, tb):
                return True
            tb = tb.tb_next
        return False

    def is_important_frame(self, important_module, tb):
        g = tb.tb_frame.f_globals
        if '__name__' not in g:
            return False
        module_name = g['__name__']
        if module_name == important_module:
            return True
        filename = os.path.abspath(tb.tb_frame.f_code.co_filename)
        test_string = os.path.sep + important_module.replace('.', os.path.sep)
        return (test_string + '.py' in filename or
                test_string + os.path.sep + '__init__.py' in filename)
