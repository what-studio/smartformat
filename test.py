# -*- coding: utf-8 -*-
from smartformat.dotnet import DotNetFormatter
from smartformat.smart import SmartFormatter


class TestFormatter(object):

    formatter_class = NotImplemented

    def format(self, locale, *args, **kwargs):
        formatter = self.formatter_class(locale)
        return formatter.format(*args, **kwargs)


class TestDotNetFormatter(TestFormatter):

    formatter_class = DotNetFormatter

    def test_no_format_spec(self):
        assert self.format('en_US', u'{0}', 123) == u'123'

    def test_currency(self):
        assert self.format('en_US', u'{0:c}', 123.456) == u'$123.46'
        assert self.format('fr_FR', u'{0:c}', 123.456) == u'123,46\xa0€'
        assert self.format('ja_JP', u'{0:c}', 123.456) == u'￥123'
        assert self.format('fr_FR', u'{0:c3}', -123.456) == u'-123,456\xa0€'
        assert self.format('ja_JP', u'{0:c3}', -123.456) == u'-￥123.456'

    def test_number(self):
        assert self.format('en_US', u'{0:n}', 1234.567) == u'1,234.57'
        assert self.format('ru_RU', u'{0:n}', 1234.567) == u'1\xa0234,57'
        assert self.format('en_US', u'{0:n1}', 1234) == u'1,234.0'
        assert self.format('ru_RU', u'{0:n1}', 1234) == u'1\xa0234,0'
        assert self.format('en_US', u'{0:n3}', -1234.56) == u'-1,234.560'
        assert self.format('ru_RU', u'{0:n3}', -1234.56) == u'-1\xa0234,560'

    def test_percent(self):
        assert self.format('en_US', u'{0:p}', 1) == u'100.00%'
        assert self.format('fr_FR', u'{0:p}', 1) == u'100,00%'
        assert self.format('en_US', u'{0:p1}', -0.39678) == u'-39.7%'
        assert self.format('fr_FR', u'{0:p1}', -0.39678) == u'-39,7%'


class TestSmartFormatter(TestFormatter):

    formatter_class = SmartFormatter

    def assert_formats(self, locale, format_string, expectations=None):
        if expectations is None:
            format_string, expectations = locale, format_string
            locale = None
        for args, expected in expectations.items():
            if not isinstance(args, tuple):
                args = (args,)
            assert self.format(locale, format_string, *args) == expected


class TestPlural(TestSmartFormatter):

    def test_english(self):
        self.assert_formats('en_US',  # noqa
            u'There {0:is|are} {0} {0:item|items} remaining', {
               # -1: u'There are -1 items remaining',
                  0: u'There are 0 items remaining',
              # 0.5: u'There are 0.5 items remaining',
                  1: u'There is 1 item remaining',
              # 1.5: u'There are 1.5 items remaining',
                  2: u'There are 2 items remaining',
                 11: u'There are 11 items remaining',
            }
        )

    def test_turkish(self):
        self.assert_formats('tr_TR',  # noqa
            u'{0} nesne kaldı.', {
                0: u'0 nesne kaldı.',
                1: u'1 nesne kaldı.',
                2: u'2 nesne kaldı.',
            }
        )
        self.assert_formats('tr',  # noqa
            u'Seçili {0:nesneyi|nesneleri} silmek istiyor musunuz?', {
                 0: u'Seçili nesneleri silmek istiyor musunuz?',
                 1: u'Seçili nesneyi silmek istiyor musunuz?',
                 2: u'Seçili nesneleri silmek istiyor musunuz?',
                11: u'Seçili nesneleri silmek istiyor musunuz?',
            }
        )

    def test_russian(self):
        self.assert_formats('ru_RU',  # noqa
            u'Я купил {0} {0:банан|банана|бананов}.', {
                  0: u'Я купил 0 бананов.',
                  1: u'Я купил 1 банан.',
                  2: u'Я купил 2 банана.',
                 11: u'Я купил 11 бананов.',
                 20: u'Я купил 20 бананов.',
                 21: u'Я купил 21 банан.',
                 22: u'Я купил 22 банана.',
                 25: u'Я купил 25 бананов.',
                120: u'Я купил 120 бананов.',
                121: u'Я купил 121 банан.',
                122: u'Я купил 122 банана.',
                125: u'Я купил 125 бананов.',
            }
        )

    def test_specific_language(self):
        format_string = (u'{0} {0:plural(en):one|many} {0:p(ko):많이} '
                         u'{0:plural(pl):miesiąc|miesiące|miesięcy}')
        assert self.format(None, format_string, 2) == u'2 many 많이 miesiące'


class TestChoose(TestSmartFormatter):

    def test_int_str_bool(self):
        self.assert_formats(u'{0:choose(1|2|3):one|two|three}', {
            1: u'one',
            2: u'two',
            3: u'three',
        })
        self.assert_formats(u'{0:choose(3|2|1):three|two|one}', {
            1: u'one',
            2: u'two',
            3: u'three',
        })
        self.assert_formats(u'{0:choose(1|2|3):one|two|three}', {
            u'1': u'one',
            u'2': u'two',
            u'3': u'three',
        })
        self.assert_formats(u'{0:choose(A|B|C):Alpha|Bravo|Charlie}', {
            u'A': u'Alpha',
            u'B': u'Bravo',
            u'C': u'Charlie',
        })
        self.assert_formats(u'{0:choose(True|False):yep|nope}', {
            True: u'yep',
            False: u'nope',
        })
