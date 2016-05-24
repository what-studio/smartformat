# -*- coding: utf-8 -*-
import babel

from smartformat.dotnet import DotNetFormatter


en_us = babel.Locale.parse('en_US')
ru_ru = babel.Locale.parse('ru_RU')
fr_fr = babel.Locale.parse('fr_FR')
ja_jp = babel.Locale.parse('ja_JP')


def test_dot_net_currency_format():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:c}', 123.456) == u'$123.46'
    assert F(fr_fr).format(u'{0:c}', 123.456) == u'123,46\xa0€'
    # assert F(ja_jp).format(u'{0:c}', 123.456) == u'¥123'
    assert F(ja_jp).format(u'{0:c}', 123.456) == u'￥123'
    # assert F(en_us).format(u'{0:c3}', -123.456) == u'($123.456)'
    assert F(fr_fr).format(u'{0:c3}', -123.456) == u'-123,456\xa0€'
    assert F(ja_jp).format(u'{0:c3}', -123.456) == u'-￥123.456'


def test_dot_net_number_format():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:n}', 1234.567) == u'1,234.57'
    assert F(ru_ru).format(u'{0:n}', 1234.567) == u'1\xa0234,57'
    assert F(en_us).format(u'{0:n1}', 1234) == u'1,234.0'
    assert F(ru_ru).format(u'{0:n1}', 1234) == u'1\xa0234,0'
    assert F(en_us).format(u'{0:n3}', -1234.56) == u'-1,234.560'
    assert F(ru_ru).format(u'{0:n3}', -1234.56) == u'-1\xa0234,560'


def test_dot_net_percent_format():
    F = DotNetFormatter
    assert F(en_us).format(u'{0:p}', 1) == u'100.00%'
    assert F(fr_fr).format(u'{0:p}', 1) == u'100,00%'
    assert F(en_us).format(u'{0:p1}', -0.39678) == u'-39.7%'
    assert F(fr_fr).format(u'{0:p1}', -0.39678) == u'-39,7%'
