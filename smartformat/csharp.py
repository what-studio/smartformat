import string


class CSharpFormatter(string.Formatter):

    def parse(self, *args):
        print 'parse', args
        return super(CSharpFormatter, self).parse(*args)

    def get_field(self, *args):
        print 'get_field', args
        return super(CSharpFormatter, self).get_field(*args)

    def get_value(self, *args):
        print 'get_value', args
        return super(CSharpFormatter, self).get_value(*args)

    def check_unused_args(self, *args):
        print 'check_unused_args', args
        return super(CSharpFormatter, self).check_unused_args(*args)

    def format_field(self, *args):
        print 'format_field', args
        return super(CSharpFormatter, self).format_field(*args)

    def convert_field(self, *args):
        print 'convert_field', args
        return super(CSharpFormatter, self).convert_field(*args)
