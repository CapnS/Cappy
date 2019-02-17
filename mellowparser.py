from rply import ParserGenerator
from mellowast import *

class Parser:
    def __init__(self):
        self.pg = ParserGenerator(
            ['NUMBER', '(', ')',
            'SUM', 'SUB', 'MUL', 'DIV', 'PRINT', 
            '=', 'NEWLINE', 'IDENTIFIER','STRING',
            '$end', 'IF','==', '!=', '>=', '<=', '<', '>',
            'COLON', 'ELSE', 'ELIF', 'DEF', 'END', 'SLEEP',
            ',', 'open', 'read', '.', 'return'
            ],
            precedence=[
                ('left', ['SUM', 'SUB']),
                ('left', ['MUL', 'DIV']),
                ('left', ['DEF', 'END', 'return', 'IDENTIFIER']),
                ('left', ['IF', 'COLON', 'ELIF', 'ELSE', 'NEWLINE']),
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
        def statement_full(env, p):
            try:
                p[0].gettokentype()
                return p[1]
            except AttributeError:
                return p[0]

        @self.pg.production('statement : IDENTIFIER = expression')
        def assignment(env, p):
            if isinstance(p[2], Function):
                return Assignment(Variable(p[0].value),p[2])
            return Assignment(Variable(p[0].value),p[2])

        @self.pg.production('expression : IDENTIFIER')
        def variable(env, p):
            return Variable(p[0].value)

        @self.pg.production('statement : expression')
        def statement_expr(env, p):
            return p[0]

        @self.pg.production('statement : PRINT ( expression )')
        def printsw(env, p):
            return Print(p[2])

        @self.pg.production('statement : SLEEP ( NUMBER )')
        def sleep(env, p):
            return Sleep(int(p[2].value))

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
        def binop(env, p):
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

        @self.pg.production('expression : IF expression COLON NEWLINE block END')
        def expression_if(env, p):
            return If(condition=p[1],body=p[4])

        @self.pg.production('expression : IF expression COLON NEWLINE block ELSE COLON NEWLINE block END')
        def expression_if_else(env, p):
            return If(condition=p[1],body=p[4],else_body=p[8])

        @self.pg.production('expression : IF expression COLON NEWLINE block ELIF expression COLON NEWLINE block END')
        def expression_if_elif(env, p):
            return If(condition=p[1],body=p[4], elif_condition=p[6], elif_body=p[9])

        @self.pg.production('expression : IF expression COLON NEWLINE block ELIF expression COLON NEWLINE block ELSE COLON NEWLINE block END')
        def expression_if_elif_else(env, p):
            return If(condition=p[1], body=p[4], elif_condition=p[6], elif_body=p[9], else_body=p[13])

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

        @self.pg.production('block : statement_full')
        def block_expr(env, p):
            return Block(p[0])

        @self.pg.production('block : statement_full block')
        def block_expr_block(env, p):
            if type(p[1]) is Block:
                b = p[1]
            else:
                b = Block(p[1])
            
            b.add_statement(p[0])
            return b

        @self.pg.production("expression : IDENTIFIER ( )")
        def function_call(env, p):
            return Function(p[0].value) 

        @self.pg.production("expression : IDENTIFIER ( expressionlist )")
        def function_call(env, p):
            have = list(p[2].statements)
            env.args[1] = have
            return Function(p[0].value, Array(p[2]))

        @self.pg.production("defstatement : DEF IDENTIFIER")
        def defstatement(env, p):
            return p[1].value

        @self.pg.production("statement : defstatement ( ) COLON NEWLINE block END")
        def function_assign(env, p):
            return AssignmentFunction(p[0], p[5], None)

        @self.pg.production("statement : defstatement ( args ) COLON NEWLINE block END")
        def function_assign(env, p):
            need = list(x.name for x in p[2].statements)
            env.args[0] = need
            func = AssignmentFunction(p[0], p[6], Array(p[2]))
            return func

        @self.pg.production('args : IDENTIFIER')
        @self.pg.production('args : IDENTIFIER ,')
        def arglist_single(env, p):
            return InnerArray([Variable(p[0].value)])

        @self.pg.production('args : IDENTIFIER , args')
        def arglist(env, p):
            p[2].append(Variable(p[0].value))
            return p[2]

        @self.pg.production('expressionlist : expression')
        @self.pg.production('expressionlist : expression ,')
        def expressionlist_single(env, p):
            return InnerArray([p[0]])

        @self.pg.production('expressionlist : expression , expressionlist')
        def arglist(env, p):
            p[2].append(p[0])
            return p[2]

        @self.pg.production('expression : open ( STRING )')
        @self.pg.production('openfile : open ( STRING )')
        def openfile(env, p):
            return Open(p[2].value)
        
        @self.pg.production('expression : openfile . read ( )')
        @self.pg.production('expression : IDENTIFIER . read ( )')
        def readfile(env, p):
            if type(p[0]) == Open:
                return Read(Open(p[0].filepath).eval(env))
            else:
                return Read(Variable(p[0].value))

        @self.pg.production('statement : returning')
        def returning(env, p):
            return p[0]
        
        @self.pg.production('returning : return expression')
        def returning(env, p):
            return Return(p[1])

        @self.pg.error
        def error_handler(env, token):
            print(token)
            print(token.getsourcepos())
            raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

    def get_parser(self):
        return self.pg.build()