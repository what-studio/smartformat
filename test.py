# -*- coding: utf-8 -*-
import babel
import pytest

from smartformat.dotnet import DotNetFormatter
from smartformat.smart import SmartFormatter


en_us = babel.Locale.parse('en_US')
ru_ru = babel.Locale.parse('ru_RU')
fr_fr = babel.Locale.parse('fr_FR')
ja_jp = babel.Locale.parse('ja_JP')


def assert_format_results(formatter, template, expectations):
    for args, expected in expectations:
        assert formatter.format(template, *args) == expected


def test_dot_net_format_without_format_spec():
    F = DotNetFormatter
    assert F(en_us).format(u'{0}', 123) == u'123'


def test_dot_net_format_currency():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:c}', 123.456) == u'$123.46'
    assert F(fr_fr).format(u'{0:c}', 123.456) == u'123,46\xa0€'
    # assert F(ja_jp).format(u'{0:c}', 123.456) == u'¥123'
    assert F(ja_jp).format(u'{0:c}', 123.456) == u'￥123'
    # assert F(en_us).format(u'{0:c3}', -123.456) == u'($123.456)'
    assert F(fr_fr).format(u'{0:c3}', -123.456) == u'-123,456\xa0€'
    assert F(ja_jp).format(u'{0:c3}', -123.456) == u'-￥123.456'


def test_dot_net_format_number():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:n}', 1234.567) == u'1,234.57'
    assert F(ru_ru).format(u'{0:n}', 1234.567) == u'1\xa0234,57'
    assert F(en_us).format(u'{0:n1}', 1234) == u'1,234.0'
    assert F(ru_ru).format(u'{0:n1}', 1234) == u'1\xa0234,0'
    assert F(en_us).format(u'{0:n3}', -1234.56) == u'-1,234.560'
    assert F(ru_ru).format(u'{0:n3}', -1234.56) == u'-1\xa0234,560'


def test_dot_net_format_percent():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:p}', 1) == u'100.00%'
    assert F(fr_fr).format(u'{0:p}', 1) == u'100,00%'
    assert F(en_us).format(u'{0:p1}', -0.39678) == u'-39.7%'
    assert F(fr_fr).format(u'{0:p1}', -0.39678) == u'-39,7%'


def test_smart_formatter_throws_exceptions():
    f = SmartFormatter()
    with pytest.raises(IndexError):
        f.format(u'--{0}--', error=42)


def test_smart_formatter_plural():
    F = SmartFormatter
    # assert \
    #     F(en_us).format(u'You have {0} new {0:message|messages}', 1) == \
    #     u'You have 1 new message'
    # assert \
    #     F(en_us).format(u'You have {0} new {0:message|messages}', 2) == \
    #     u'You have 2 new messages'
    assert \
        F(en_us).format(u'There {0:plural:is 1 item|are {} items}.', 1) == \
        u'There is 1 item.'
    assert \
        F(en_us).format(u'There {0:plural:is 1 item|are {} items}.', 2) == \
        u'There are 2 items.'


class TestPlural(object):

    def assert_plural(self, locale, template, expectations):
        formatter = SmartFormatter(locale)
        for number, expected in expectations.items():
            assert formatter.format(template, number) == expected

    def test_english(self):
        self.assert_plural('en_US',  # noqa
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
        self.assert_plural('tr_TR',  # noqa
            u'{0} nesne kaldı.', {
                0: u'0 nesne kaldı.',
                1: u'1 nesne kaldı.',
                2: u'2 nesne kaldı.',
            }
        )
        self.assert_plural('tr',  # noqa
            u'Seçili {0:nesneyi|nesneleri} silmek istiyor musunuz?', {
                 0: u'Seçili nesneleri silmek istiyor musunuz?',
                 1: u'Seçili nesneyi silmek istiyor musunuz?',
                 2: u'Seçili nesneleri silmek istiyor musunuz?',
                11: u'Seçili nesneleri silmek istiyor musunuz?',
            }
        )

    def test_russian(self):
        self.assert_plural('ru_RU',  # noqa
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
