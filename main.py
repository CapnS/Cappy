from capnlexer import Lexer
from capnparser import Parser
from capnenv import Environment

with open("C:/Users/zacha/OneDrive/Documents/Python/Capy/test.capn") as f:
    text = f.read().encode("unicode_escape").decode("utf-8").replace('    ', '\\t')

env = Environment()
lexer = Lexer().get_lexer()
parser = Parser().get_parser()
parser.parse(lexer.lex(text), env).eval(env)
