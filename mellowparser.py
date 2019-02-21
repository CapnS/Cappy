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
            ',', 'open', 'read', '.', 'return', 'import',
            '{', '}', 'AND', 'await', '@', 'from', '[', ']'
            ],
            precedence=[
                ('left', ['SUM', 'SUB']),
                ('left', ['MUL', 'DIV']),
                ('left', ['DEF', 'END', 'return', 'IDENTIFIER']),
                ('left', ['IF', 'COLON', 'ELIF', 'ELSE', 'NEWLINE']),
                ('left', ['==', '!=', '>=','>', '<', '<=',]),
                ('left', ['=']),
                ('left', ['{', '}'])
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

        @self.pg.production('expression : IDENTIFIER [ expression ]')
        def index(env, p):
            return Index(Variable(p[0].value),p[2].value)
            
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

        @self.pg.production("function : IDENTIFIER ( )")
        def function_call(env, p):
            return Function(p[0].value) 

        @self.pg.production("function : IDENTIFIER ( args )")
        def function_callargs(env, p):
            have = list(p[2].statements)
            env.args[1] = have
            return Function(p[0].value, Array(p[2]))
        
        @self.pg.production('function : IDENTIFIER . IDENTIFIER ( ) ')
        def importedfunc(env, p):
            return ImportedFunction(p[0].value, p[2].value)
        
        @self.pg.production('function : IDENTIFIER . IDENTIFIER ( args ) ')
        def importedfuncargs(env, p):
            return ImportedFunction(p[0].value, p[2].value, p[4])

        @self.pg.production('function : IDENTIFIER . IDENTIFIER ( args AND kwargs ) ')
        def importedfuncboth(env, p):
            return ImportedFunction(p[0].value, p[2].value, p[4], p[6])

        @self.pg.production('function : IDENTIFIER . IDENTIFIER ( kwargs ) ')
        def importedfunckwargs(env, p):
            return ImportedFunction(p[0].value, p[2].value, None, p[4])

        @self.pg.production('expression : function')
        def function(env, p):
            return p[0]
        
        @self.pg.production('expression : await function')
        def awaitfunction(env, p):
            return Await(p[1])

        @self.pg.production('funcstatement : defstatement ( ) COLON NEWLINE block END')
        def funcstate(env, p):
            return AssignmentFunction(p[0], p[5], None)

        @self.pg.production('statement : @ IDENTIFIER . IDENTIFIER NEWLINE funcstatement')
        def blank_deco(env, p ):
            return DecoratedFunction(p[1].value, p[3].value, p[5], False, None, None)

        @self.pg.production('statement : @ IDENTIFIER . IDENTIFIER ( ) NEWLINE funcstatement')
        def none_deco(env, p ):
            return DecoratedFunction(p[1].value, p[3].value, p[7], True, None, None)

        @self.pg.production('statement : @ IDENTIFIER . IDENTIFIER ( args AND kwargs ) NEWLINE funcstatement')
        def both_deco(env, p ):
            return DecoratedFunction(p[1].value, p[3].value, p[10], True, p[5], p[7])

        @self.pg.production('statement : @ IDENTIFIER . IDENTIFIER ( kwargs ) NEWLINE funcstatement')
        def kwargs_deco(env, p ):
            return DecoratedFunction(p[1].value, p[3].value, p[8], True, None, p[5])

        @self.pg.production('statement : @ IDENTIFIER . IDENTIFIER ( args ) NEWLINE funcstatement')
        def args_deco(env, p ):
            return DecoratedFunction(p[1].value, p[3].value, p[8], True, p[5], None)

        @self.pg.production("defstatement : DEF IDENTIFIER")
        def defstatement(env, p):
            return p[1].value

        @self.pg.production("statement : funcstatement")
        def function_assign(env, p):
            return p[0]

        @self.pg.production("funcstatement : defstatement ( args ) COLON NEWLINE block END")
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

        @self.pg.production('args : expression')
        @self.pg.production('args : expression ,')
        def args_single(env, p):
            return InnerArray([p[0]])

        @self.pg.production('args : expression , args')
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
                return Read(Open(p[0].filepath))
            else:
                return Read(Variable(p[0].value))

        @self.pg.production('statement : returning')
        def returning(env, p):
            return p[0]
        
        @self.pg.production('returning : return expression')
        def returnz(env, p):
            return Return(p[1])

        @self.pg.production('statement : import idlist')
        def importing(env, p):
            return Import(p[1], None)
        
        @self.pg.production('idlist : IDENTIFIER')
        @self.pg.production('idlist : IDENTIFIER . idlist')
        def importz(env, p):
            try:
                return p[0].value +  "." + p[2]
            except IndexError:
                return p[0].value

        @self.pg.production('statement : from idlist import IDENTIFIER')
        def imported(env, p):
            return Import(p[3].value, p[1])    

        @self.pg.production('expression : IDENTIFIER . IDENTIFIER')
        def importez(env, p):
            return GetAttr(p[0].value, p[2].value)

        @self.pg.production('kwargs : IDENTIFIER = expression')
        @self.pg.production('kwargs : IDENTIFIER = expression ,')
        def kwargs_single(state, p):
            return InnerDict({ p[0].value: p[2] })

        @self.pg.production('kwargs : IDENTIFIER = expression , kwargs')
        def arglist(state, p):
            p[4].update(p[0].value,p[2])
            return p[4]

        @self.pg.production('dict : expression COLON expression')
        @self.pg.production('dict : expression COLON expression ,')
        def kwargs_single(state, p):
            return InnerDict({ p[0]: p[2] })

        @self.pg.production('dict : expression COLON expression , dict')
        def arglist(state, p):
            p[4].update(p[0],p[2])
            return p[4]

        @self.pg.production('expression : { dict }')
        def expression_dict(state, p):
            return Dict(p[1])

        @self.pg.error
        def error_handler(env, token):
            if token.gettokentype() == "$end":
                raise SyntaxError("Ran into EoF while still parsing. Check to make sure you have end after every if/def")
            print(token.getsourcepos())
            raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

    def get_parser(self):
        return self.pg.build()