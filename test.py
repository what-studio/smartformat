import babel

from smartformat import CSharpFormatter


en_us = babel.Locale.parse('en_US')
ru_ru = babel.Locale.parse('ru_RU')
fr_fr = babel.Locale.parse('fr_FR')
ja_jp = babel.Locale.parse('ja_JP')


def test_csharp_format():
    F = CSharpFormatter
    assert F(en_us).format(u'{0:n}', 1234.567) == u'1,234.57'
    assert F(ru_ru).format(u'{0:n}', 1234.567) == u'1 234,57'
    assert F(en_us).format(u'{0:n1}', 1234) == u'1,234.0'
    assert F(ru_ru).format(u'{0:n1}', 1234) == u'1 234,0'
    assert F(en_us).format(u'{0:n3}', -1234.56) == u'-1,234.560'
    assert F(ru_ru).format(u'{0:n3}', -1234.56) == u'-1 234,560'
