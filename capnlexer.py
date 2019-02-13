from rply import LexerGenerator


class Lexer:
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        self.lexer.add('PRINT', r'print')
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')
        self.lexer.add('SUM', r'\+')
        self.lexer.add('SUB', r'\-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add("DIV", r'\/')
        self.lexer.add('NUMBER', r'\d+')
        self.lexer.add('STRING', r'(""".*?""")|(".*?")|(\'.*?\')')
        self.lexer.add('IF', r'if')
        self.lexer.add('ELSE', r'else')
        self.lexer.add('ELIF', r'elif')
        self.lexer.add('DEF', r'def')
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')  
        self.lexer.add('NEWLINE', r'\\n')
        self.lexer.add('COLON', r':')
        self.lexer.add('TAB', r'\\t')
        self.lexer.add('==', r'==')
        self.lexer.add('!=', r'!=')
        self.lexer.add('>=', r'>=')
        self.lexer.add('<=', r'<=')
        self.lexer.add('>', r'>')
        self.lexer.add('<', r'<')
        self.lexer.add('=', r'=')
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()