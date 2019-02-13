from rply import ParserGenerator
from capnast import *

class Parser:
    def __init__(self):
        self.pg = ParserGenerator(
            ['NUMBER', 'OPEN_PAREN', 'CLOSE_PAREN',
            'SUM', 'SUB', 'MUL', 'DIV', 'PRINT', 
            '=', 'NEWLINE', 'IDENTIFIER','STRING',
            '$end', 'IF','==', '!=', '>=', '<=', '<', '>',
            'COLON', 'TAB', 'ELSE', 'ELIF', 'DEF'
            ],
            precedence=[
                ('left', ['SUM', 'SUB']),
                ('left', ['MUL', 'DIV']),
                ('left', ['DEF', 'IDENTIFIER']),
                ('left', ['IF', 'ELIF', 'ELSE', 'COLON', 'TAB','NEWLINE']),
                ('left', ['==', '!=', '>=','>', '<', '<=',]),
                ('left', ['='])
            ]
        )
        self.build()

    def build(self):
        @self.pg.production("main : program")
        def main_program(env, p):
            return p[0]
        
        @self.pg.production('program : statement_full')
        def program_statement(env, p):
            return Program(p[0])

        @self.pg.production('program : statement_full program')
        def program_statement_program(env, p):
            if type(p[1]) is Program:
                program = p[1]
            else:
                program = Program(p[-1])
            
            program.add_statement(p[0])
            return p[1]

        @self.pg.production('statement_full : statement NEWLINE')
        @self.pg.production('statement_full : statement $end')
        @self.pg.production('statement_full : TAB statement')
        def statement_full(env, p):
            try:
                p[0].gettokentype()
                return p[1]
            except AttributeError:
                return p[0]

        @self.pg.production('statement : IDENTIFIER = expression')
        def assignment(env, p):
            return Assignment(Variable(p[0].value),p[2])

        @self.pg.production('expression : IDENTIFIER')
        def variable(env, p):
            return Variable(p[0].value)

        @self.pg.production('statement : expression')
        @self.pg.production('statement : program')
        def statement_expr(env, p):
            return p[0]

        @self.pg.production('statement : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print(env, p):
            return Print(p[2])

        @self.pg.production('expression : NUMBER')
        def number(env, p):
            return Number(int(p[0].value))
        
        @self.pg.production('expression : STRING')
        def string(env, p):
            return String(str(p[0].value))

        @self.pg.production('expression : expression SUM expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        def binop(p):
            left = p[0]
            right = p[2]
            if p[1].gettokentype() == 'SUM':
                return Sum(left, right)
            elif p[1].gettokentype() == 'SUB':
                return Sub(left, right)
            elif p[1].gettokentype() == 'MUL':
                return Mul(left, right)
            elif p[1].gettokentype() == 'DIV':
                return Div(left, right)
            else:
                raise AssertionError('Oops, this should not be possible!')

        @self.pg.production('expression : IF expression COLON NEWLINE TAB program NEWLINE')
        @self.pg.production('expression : IF expression COLON NEWLINE TAB program $end')
        def expression_if(env, p):
            return If(condition=p[1],body=p[5])

        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELSE COLON NEWLINE TAB program NEWLINE')
        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELSE COLON NEWLINE TAB program $end')
        def expression_if_else(env, p):
            return If(condition=p[1],body=p[5],else_body=p[10])

        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELIF expression COLON NEWLINE TAB program NEWLINE')
        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELIF expression COLON NEWLINE TAB program $end')
        def expression_if_elif(env, p):
            return If(condition=p[1],body=p[5], elif_condition=p[7], elif_body=p[11])

        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELIF expression COLON NEWLINE TAB program ELSE COLON NEWLINE TAB program NEWLINE')
        @self.pg.production('expression : IF expression COLON NEWLINE TAB program ELIF expression COLON NEWLINE TAB program ELSE COLON NEWLINE TAB program $end')
        def expression_if_elif_else(env, p):
            return If(condition=p[1], body=p[5], elif_condition=p[7], elif_body=p[11], else_body=p[16])

        @self.pg.production('expression : expression != expression')
        @self.pg.production('expression : expression == expression')
        @self.pg.production('expression : expression >= expression')
        @self.pg.production('expression : expression <= expression')
        @self.pg.production('expression : expression > expression')
        @self.pg.production('expression : expression < expression')
        def expression_equality(env, p):
            left = p[0]
            right = p[2]
            check = p[1]
            
            if check.gettokentype() == '==':
                return Equal(left, right)
            elif check.gettokentype() == '!=':
                return NotEqual(left, right)
            elif check.gettokentype() == '>=':
                return GreaterThanEqual(left, right)
            elif check.gettokentype() == '<=':
                return LessThanEqual(left, right)
            elif check.gettokentype() == '>':
                return GreaterThan(left, right)
            elif check.gettokentype() == '<':
                return LessThan(left, right)
            else:
                raise ValueError("Shouldn't be possible")
        
        @self.pg.production("statement : DEF IDENTIFIER OPEN_PAREN CLOSE_PAREN COLON NEWLINE TAB program NEWLINE")
        @self.pg.production("statement : DEF IDENTIFIER OPEN_PAREN CLOSE_PAREN COLON NEWLINE TAB program $end")
        def function_assign(env, p):
            return AssignmentFunction(Function(p[1].value, env), p[8], env)

        @self.pg.production("statement : IDENTIFIER OPEN_PAREN CLOSE_PAREN NEWLINE")
        @self.pg.production("statement : IDENTIFIER OPEN_PAREN CLOSE_PAREN $end")
        def function_call(env, p):
            return Call(Function(p[0].value, env), env)

        @self.pg.error
        def error_handler(env, token):
            raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

    def get_parser(self):
        return self.pg.build()