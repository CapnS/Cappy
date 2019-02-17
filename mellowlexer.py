from rply import LexerGenerator, LexingError
import re

class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('STRING', r'(""".*?""")|(".*?")|(\'.*?\')')
        self.lexer.add('PRINT', r'print')
        self.lexer.add('SLEEP', r'sleep')
        self.lexer.add('END', r'end')
        self.lexer.add('open', r'open')
        self.lexer.add('read', r'read')
        self.lexer.add('return', r'return')
        self.lexer.add(',', r',')
        self.lexer.add('.', r'\.')
        self.lexer.add('(', r'\(')
        self.lexer.add(')', r'\)')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add("DIV", r'\/')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('IF', r'if')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('ELIF', r'elif')
        self.lexer.add('DEF', r'def')
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')  
        self.lexer.add('NEWLINE', r'\\n')
        self.lexer.add('COLON', r':')
        self.lexer.add('==', r'==')
        self.lexer.add('!=', r'!=')
        self.lexer.add('>=', r'>=')
        self.lexer.add('<=', r'<=')
        self.lexer.add('>', r'>')
        self.lexer.add('<', r'<')
        self.lexer.add('=', r'=')
        self.lexer.ignore(r'\s+')

    def lex(self, source):
        self._add_tokens()
        lexer = self.lexer.build()
        comments = r'#[^\\n]*(?:\\n|\Z|\\n)'
        comment = re.search(comments,source)
        commented = False
        while comment is not None:
            commented = True
            start, end = comment.span(0)
            assert start >= 0 and end >= 0
            source = source[0:start] + source[end:]
            comment = re.search(comments,source)
        try:
            lex = lexer.lex(source)
            if commented:
                for t in lex:
                    t.value
        except:
            source = source.replace('\\n', '\n')
            comments = r'#[^\n]*'
            comment = re.search(comments,source)
            while comment is not None:
                start, end = comment.span(0)
                assert start >= 0 and end >= 0
                source = source[0:start] + source[end:]
                comment = re.search(comments,source)
            source = source.replace('\n', '\\n')
            return lexer.lex(source)
        else:
            return lex

