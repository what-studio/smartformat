# -*- coding: utf-8 -*-
from datetime import date

from babel import Locale, UnknownLocaleError
import pytest

from smartformat.dotnet import DotNetFormatter
from smartformat.local import LocalFormatter
from smartformat.smart import SmartFormatter


class Gender(object):

    def __init__(self, name):
        self.name = name


Gender.male = Gender('male')
Gender.female = Gender('female')


class Person(object):

    def __init__(self, name, gender, birthday, address):
        self.name = name
        self.gender = gender
        self.birthday = birthday
        self.address = address
        self.friends = []
        self.spouse = None

    def marry(self, spouse):
        self.spouse, spouse.spouse = spouse, self

    def parse_name(self):
        parts = self.name.split(' ', 2)
        assert len(parts) >= 2
        if len(parts) == 2:
            return (parts[0], None, parts[1])
        else:
            return (parts[0], parts[1], parts[2])

    @property
    def first_name(self):
        return self.parse_name()[0]

    @property
    def middle_name(self):
        return self.parse_name()[1]

    @property
    def last_name(self):
        return self.parse_name()[2]


@pytest.fixture
def michael():
    michael = Person(u'Michael Scott', Gender.male, date(1970, 3, 3),
                     u'333 Third St, Scranton, PA 18447')
    jim = Person(u'Jim Halpert', Gender.male, date(1979, 1, 1),
                 u'111 First St, Scranton, PA 18447')
    pam = Person(u'Pam Halpert', Gender.female, date(1980, 1, 1),
                 u'111 First St, Scranton, PA 18447')
    dwight = Person(u'Dwight K Schrute', Gender.male, date(1978, 2, 2),
                    u'222 Second St, Scranton, PA 18447')
    michael.friends.extend([jim, pam, dwight])
    jim.friends.extend([dwight, michael])
    pam.friends.extend([dwight, michael])
    jim.marry(pam)
    dwight.friends.append(michael)
    return michael


class TestFormatter(object):

    formatter_class = NotImplemented

    def format(self, locale, *args, **kwargs):
        try:
            locale = Locale.parse(locale)
        except (ValueError, UnknownLocaleError):
            args = (locale,) + args
            locale = None
        formatter = self.formatter_class(locale)
        return formatter.format(*args, **kwargs)


class TestLocalFormatter(TestFormatter):

    formatter_class = LocalFormatter

    @pytest.mark.parametrize('format_string', [u'{0}', u'{0:f}', u'{0:d}'])
    @pytest.mark.parametrize('n', [1, 100000, 42, 123456789, 123456.123456,
                                   float('nan'), float('inf')])
    def test_same(self, format_string, n):
        try:
            expected = format_string.format(n)
        except BaseException as exc:
            with pytest.raises(type(exc)):
                self.format(format_string, n)
        else:
            assert self.format(format_string, n) == expected

    def test_decimal(self):
        assert self.format('ru_RU', u'{0:d}', 12345) == u'12345'
        assert self.format('ru_RU', u'{0:,d}', 12345) == u'12\xa0345'
        assert self.format('hi_IN', u'{0:,d}', 123456789) == u'12,34,56,789'
        assert self.format('hi_IN', u'{0:+,d}', 123456789) == u'+12,34,56,789'
        assert self.format('hi_IN', u'{0: ,d}', 123456789) == u' 12,34,56,789'

    def test_float(self):
        assert \
            self.format('hi_IN', u'{0:,.5f}', 123456.123456) == \
            u'1,23,456.12346'
        assert \
            self.format('hi_IN', u'{0:^020,.5f}', 123456.123456) == \
            u'0001,23,456.12346000'
        assert \
            self.format('hi_IN', u'{0:_^20,.5f}', 123456.123456) == \
            u'___1,23,456.12346___'
        assert \
            self.format('hi_IN', u'{0:_<20,.5f}', 123456.123456) == \
            u'1,23,456.12346______'
        assert \
            self.format('hi_IN', u'{0:_>20,.5f}', 123456.123456) == \
            u'______1,23,456.12346'

    def test_percent(self):
        assert self.format('ru_RU', u'{0:%}', 0.12345) == u'12,345000%'
        assert \
            self.format('ru_RU', u'{0:020%}', 0.12345) == \
            u'000000000012,345000%'
        assert \
            self.format('ru_RU', u'{0:020,%}', 0.12345) == \
            u'000000000012,345000%'
        assert \
            self.format('ru_RU', u'{0:020,%}', 12345) == \
            u'0001\xa0234\xa0500,000000%'


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

    def test_decimal(self):
        assert self.format(u'{0:d}', 1234) == u'1234'
        assert self.format(u'{0:d6}', -1234) == u'-001234'

    def test_scientific(self):
        # parse_pattern('0.######E+000').apply(1052.0329112756, 'en_US')
        assert \
            self.format('en_US', u'{0:E}', 1052.0329112756) == u'1.052033E+003'
        assert \
            self.format('fr_FR', u'{0:e}', 1052.0329112756) == u'1,052033e+003'
        assert \
            self.format('en_US', u'{0:e2}', -1052.0329112756) == u'-1.05e+003'
        assert \
            self.format('fr_FR', u'{0:E2}', -1052.0329112756) == u'-1,05E+003'

    def test_float(self):
        assert self.format('en_US', u'{0:f}', 1234.567) == u'1234.57'
        assert self.format('de_DE', u'{0:f}', 1234.567) == u'1234,57'
        assert self.format('en_US', u'{0:f1}', 1234) == u'1234.0'
        assert self.format('de_DE', u'{0:f1}', 1234) == u'1234,0'
        assert self.format('en_US', u'{0:f4}', -1234.56) == u'-1234.5600'
        assert self.format('de_DE', u'{0:f4}', -1234.56) == u'-1234,5600'

    @pytest.mark.xfail
    def test_general(self):
        assert self.format('en_US', u'{0:g}', -123.456) == u'-123.456'
        assert self.format('sv_SE', u'{0:g}', -123.456) == u'-123,456'
        assert self.format('en_US', u'{0:g4}', -123.4546) == u'-123.5'
        assert self.format('sv_SE', u'{0:g4}', -123.4546) == u'-123,5'
        assert \
            self.format('en_US', u'{0:G}', -1.234567890e-25) == \
            u'-1.23456789E-25'
        assert \
            self.format('en_US', u'{0:g}', -1.234567890e-25) == \
            u'-1.23456789e-25'
        assert \
            self.format('sv_SE', u'{0:G}', -1.234567890e-25) == \
            u'-1,23456789E-25'

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
        assert self.format('fr_FR', u'{0:p1}', -0.39678) == u'-39,7%'

    def test_hexadecimal(self):
        assert self.format(u'{0:X}', 255) == u'FF'
        assert self.format(u'{0:x}', -1) == u'ff'
        assert self.format(u'{0:x4}', 255) == u'00ff'
        assert self.format(u'{0:X4}', -1) == u'00FF'
        assert self.format(u'{0:x}', 0x2045e) == u'2045e'
        assert self.format(u'{0:X}', 0x2045e) == u'2045E'
        assert self.format(u'{0:X8}', 0x2045e) == u'0002045E'
        assert self.format(u'{0:X}', 123456789) == u'75BCD15'
        assert self.format(u'{0:X2}', 123456789) == u'75BCD15'

    def test_custom(self):
        assert self.format(u'{0:0.##}', 256.583) == u'256.58'
        assert self.format(u'{0:0.##}', 256.586) == u'256.59'
        assert self.format(u'{0:0.##}', 256.58) == u'256.58'
        assert self.format(u'{0:0.##}', 256.5) == u'256.5'
        assert self.format(u'{0:0.##}', 256.0) == u'256'
        assert self.format(u'{0:0}', 12345.6789) == u'12346'
        assert self.format(u'{0:00}', 1) == u'01'
        assert self.format(u'~!{0:__}!~', 42) == u'~!__!~'
        assert self.format(u'~!{0:_0.0_}!~', 42) == u'~!_42.0_!~'

    def test_unknown_spec(self):
        assert self.format(u'~!{0:\x00}!~', 'Smart') == u'~!Smart!~'


class TestSmartFormatter(TestFormatter):

    formatter_class = SmartFormatter

    def assert_format(self, locale, format_string, args, expected=None):
        """Asserts that a formatted string is same with expected string."""
        if expected is None:
            format_string, args, expected = locale, format_string, args
            locale = None
        if not isinstance(args, tuple):
            args = (args,)
        assert self.format(locale, format_string, *args) == expected

    def assert_formats(self, locale, format_string, expectations=None):
        """Asserts formatted strings by multiple arguments."""
        if expectations is None:
            format_string, expectations = locale, format_string
            locale = None
        for args, expected in expectations.items():
            self.assert_format(locale, format_string, args, expected)


class TestParsing(TestSmartFormatter):

    def test_nested(self):
        self.assert_format('en_US', u'{:A{}|B{}}', 123, u'B123')
        self.assert_format('en_US', u'{:A{{{}}}|B{{{}}}}', 123, u'B{123}')


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
        xx = self.assert_formats
        xx(u'{0:choose(1|2|3):one|two|three}', {
            1: u'one', 2: u'two', 3: u'three',
        })
        xx(u'{0:choose(3|2|1):three|two|one}', {
            1: u'one', 2: u'two', 3: u'three',
        })
        xx(u'{0:choose(1|2|3):one|two|three}', {
            u'1': u'one', u'2': u'two', u'3': u'three',
        })
        xx(u'{0:choose(A|B|C):Alpha|Bravo|Charlie}', {
            u'A': u'Alpha', u'B': u'Bravo', u'C': u'Charlie',
        })
        xx(u'{0:choose(True|False):yep|nope}', {
            True: u'yep', False: u'nope',
        })

    def test_case_sensitive(self):
        x = self.assert_format
        x(u'{0:choose(true|True):one|two|default}', True, u'two')
        x(u'{0:choose(true|TRUE):one|two|default}', True, u'default')
        x(u'{0:choose(string|String):one|two|default}', 'String', u'two')
        x(u'{0:choose(string|STRING):one|two|default}', 'String', u'default')

    def test_default_to_last(self):
        x = self.assert_format
        x(u'{0:choose(1|2|3):one|two|three|default}', 1, u'one')
        x(u'{0:choose(1|2|3):one|two|three|default}', 2, u'two')
        x(u'{0:choose(1|2|3):one|two|three|default}', 3, u'three')
        x(u'{0:choose(1|2|3):one|two|three|default}', 4, u'default')
        x(u'{0:choose(1|2|3):one|two|three|default}', 99, u'default')
        x(u'{0:choose(1|2|3):one|two|three|default}', None, u'default')
        x(u'{0:choose(1|2|3):one|two|three|default}', True, u'default')
        x(u'{0:choose(1|2|3):one|two|three|default}', 'whatever', u'default')

    def test_enum(self):
        x = self.assert_format
        x(u'{0:choose(male|female):man|woman}', Gender.male, u'man')
        x(u'{0:choose(male|female):man|woman}', Gender.female, u'woman')
        x(u'{0:choose(male):man|woman}', Gender.male, u'man')
        x(u'{0:choose(male):man|woman}', Gender.female, u'woman')

    def test_null(self):
        x = self.assert_format
        x(u'{0:choose(null):nothing|{} }', None, u'nothing')
        x(u'{0:choose(null):nothing|{} }', 5, u'5 ')
        x(u'{0:choose(null|5):nothing|five|{} }', None, u'nothing')
        x(u'{0:choose(null|5):nothing|five|{} }', 5, u'five')
        x(u'{0:choose(null|5):nothing|five|{} }', 6, u'6 ')

    def test_invalid(self):
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1|2):1|2}', 99)
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1):1}', 99)

    def test_too_few_choices(self):
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1|2):1}', 1)
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1|2|3):1|2}', 1)

    def test_too_many_choices(self):
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1):1|2|3}', 1)
        with pytest.raises(ValueError):
            self.format(u'{0:choose(1|2):1|2|3|4}', 1)


class TestConditional(TestSmartFormatter):

    def test_deprecation(self):
        with pytest.raises(NotImplementedError):
            self.format(u'{0:conditional:}', 1)
        with pytest.raises(NotImplementedError):
            self.format(u'{0:cond:}', 1)


class TestList(TestSmartFormatter):

    @pytest.fixture
    def args(self, michael):
        return (
            list('ABCDE'), 'One Two Three Four Five'.split(), michael.friends,
            [date(2000, 1, 1), date(2010, 10, 10), date(5555, 5, 5)],
            list(range(1, 6)),
        )

    def test_basic(self, args):
        self.assert_format(u'{4:{}|}', args, u'12345')
        self.assert_format(u'{4:{}|,}', args, u'1,2,3,4,5')
        self.assert_format(u'{4:{}|, |, and }', args, u'1, 2, 3, 4, and 5')
        self.assert_format(u'{4:{:n2}|, |, and }', args,
                           u'1.00, 2.00, 3.00, 4.00, and 5.00')
        self.assert_format(u'{0:{}-|}', args, u'A-B-C-D-E-')
        self.assert_format(u'{0:{}|-}', args, u'A-B-C-D-E')
        self.assert_format(u'{0:{}|-|+}', args, u'A-B-C-D+E')
        self.assert_format(u'{0:({})|, |, and }', args,
                           u'(A), (B), (C), (D), and (E)')

    @pytest.mark.xfail
    def test_nested_array(self, args):
        self.assert_format(u'{2:{:{first_name}}|, }', args,
                           u'Jim, Pam, Dwight')
        self.assert_format(u'{3:{:M/d/yyyy} |}', args,
                           u'1/1/2000 10/10/2010 5/5/5555 ')
        self.assert_format(
            u"{2:{:{first_name}'s friends: {friends:{first_name}|, } }|; }",
            args,
            u"Jim's friends: Dwight, Michael ; "
            u"Pam's friends: Dwight, Michael ; "
            u"Dwight's friends: Michael ",
        )

    def test_index(self, args):
        # Index holds the current index of the iteration.
        self.assert_format(u'{0:{} = {index}|, }', args,
                           u'A = 0, B = 1, C = 2, D = 3, E = 4')
        # Index can be nested.
        # self.assert_format(u'{1:{Index}: {ToCharArray:{} = {Index}|, }|; }',
        #                    args, u'0: O = 0, n = 1, e = 2; 1: T = 0, w = 1, '
        #                    u'o = 2; 2: T = 0, h = 1, r = 2, e = 3, e = 4; '
        #                    u'3: F = 0, o = 1, u = 2, r = 3; 4: F = 0, i = '
        #                    u'1, v = 2, e = 3')
        # Index is used to synchronize 2 lists.
        # self.assert_format(u'{0:{} = {1.index}|, }', args,
        #                    u'A = One, B = Two, C = Three, '
        #                    u'D = Four, E = Five')
        # In contrast to SmartFormat.NET, `index` cannot be used out of a list
        # context.
        with pytest.raises(KeyError):
            self.format(u'{index}', args)
