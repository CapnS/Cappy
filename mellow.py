from mellowlexer import Lexer
from mellowparser import Parser
from mellowenv import Environment
import sys
import os

try:
    filepath = os.path.realpath(__file__)
    with open(os.path.join(filepath, sys.argv[1])) as f:
        text = f.read().encode("unicode_escape").decode("utf-8")
except Exception as e:
    try:
        with open("C:/Users/zacha/OneDrive/Documents/Python/Mellow/test.mlw") as f:
            text = f.read().encode("unicode_escape").decode("utf-8")
    except Exception as e:
        if type(e) == IndexError:
            print("No file passed")
            sys.exit(2)
        with open(sys.argv[1]) as f:
            text = f.read().encode("unicode_escape").decode("utf-8")

env = Environment()
lexer = Lexer()
parser = Parser().get_parser()
parser.parse(lexer.lex(text), env).eval(env)
