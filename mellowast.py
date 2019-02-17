from rply.token import BaseBox
import time

class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return int(self.value)

class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    def eval(self, env):
        return self.value

class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Sum(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) + self.right.eval(env)

class Sub(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) - self.right.eval(env)

class Mul(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) * self.right.eval(env)

class Div(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) / self.right.eval(env)

class Print:
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        print(self.value.eval(env))

class String(BaseBox):
    def __init__(self, value):
        self.value = value

    def eval(self, env):
        return self.value.strip('"\'')

class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None

    def eval(self, env):
        kwargs = dict()
        for i in range(len(env.args[1])):
            kwargs.update({env.args[0][i]:env.args[1][i]})
        if env.variables.get(self.name):
            self.value = env.variables[self.name].eval(env)
            return self.value
        elif env.arguments.get(self.name):
            self.value = env.arguments[self.name].eval(env)
            return self.value
        elif kwargs.get(self.name):
            self.value = kwargs[self.name].eval(env)
            return self.value
        raise NameError("Not yet defined")

class Assignment(BinaryOp):
    def eval(self, env):
        if isinstance(self.left,Variable):
            env.variables[self.left.name] = self.right
            return self.right.eval(env)
        else:
            raise NameError("Cannot assign to this")

class Program(BaseBox): 
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)
        self.run = False
    
    def add_statement(self, statement):
        self.statements.insert(0,statement)
        
    def eval(self, env):
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        return result
    
    def get_statements(self):
        return self.statements
    
class If(BaseBox):
    def __init__(self, *, condition, body, else_body=None, elif_condition=None, elif_body=None):
        self.condition = condition
        self.body = body
        self.else_body = else_body
        self.elif_condition = elif_condition
        self.elif_body = elif_body
        
    def eval(self, env): 
        if self.condition.eval(env): 
            return self.body.eval(env)
        elif self.elif_condition and self.elif_body and self.else_body:
            if self.elif_condition.eval(env):
                return self.elif_body.eval(env)
            else:
                if self.else_body:
                    return self.else_body.eval(env)
        elif self.elif_condition and self.elif_body:
            if self.elif_condition.eval(env):
                return self.elif_body.eval(env)
        else:
            if self.else_body:
                return self.else_body.eval(env)
        return None

class Equal(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) == self.right.eval(env)

class NotEqual(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) != self.right.eval(env)
        
class GreaterThan(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) > self.right.eval(env)

class LessThan(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) < self.right.eval(env)

class GreaterThanEqual(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) >= self.right.eval(env)

class LessThanEqual(BinaryOp):
    def eval(self, env):
        return self.left.eval(env) <= self.right.eval(env)

class Function(BaseBox):
    def __init__(self, name, args=None):
        self.name = name
        self.value = None
        self.args = args

    def eval(self, env):
        if env.functions.get(self.name):
            needed = env.functions[self.name][1]
            have = self.args.statements if self.args else []
            env.arguments = dict()
            for i in range(len(have)):
                try:
                    env.arguments.update({needed[i].name:have[i]})
                except IndexError:
                    raise TypeError(self.name + "() missing required arguments.")
            self.value = env.functions[self.name][0].eval(env)
            env.arguments = dict()
            return self.value
        raise NameError("Not yet defined")

class AssignmentFunction:
    def __init__(self, name, function, args):
        self.name = name
        self.function = function
        self.args = args.statements if args else None

    def eval(self, env):
        env.functions[self.name] = [self.function, self.args]
        return self.name

class InnerArray(BaseBox):
    def __init__(self, statements = None):
        self.statements = []
        self.values = []
        if statements:
            self.statements = statements

    def append(self, statement):
        self.statements.append(statement)


class Array(BaseBox):
    def __init__(self, inner):
        self.statements = inner.statements
        self.values = []
    
    def __len__(self):
        return len(self.statements)

    def append(self, statement):
        self.statements.append(statement)
    
    def index(self, i):
        if type(i) is Number:
            return self.values[i.value]
        raise IndexError("Cannot index with that value")

    def eval(self, env):
        
        if len(self.values) == 0:            
            for statement in self.statements:
                self.values.append(statement.eval(env))
        return self

class Block(BaseBox):
    
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)
    
    def add_statement(self, statement):
        self.statements.insert(0,statement)
    
    def get_statements(self):
        return self.statements
    
    def eval(self, env):
        result = None
        for statement in self.statements:
            result = statement.eval(env)
        return result

class Sleep:
    def __init__(self, time):
        self.time = time
    
    def eval(self, env):
        time.sleep(self.time)

class Open:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def eval(self, env):
        return open(self.filepath.strip("'\""))

class Read:
    def __init__(self, file):
        self.file = file
        self.value = None
    
    def eval(self, env):
        if self.value:
            return self.value
        elif isinstance(self.file, Variable):
            self.value = self.file.eval(env).read()
            return self.value
        else:
            self.value = self.file.read()
            return self.value

class Return:
    def __init__(self, expression):
        self.exp = expression
    
    def eval(self, env):
        return self.exp.eval(env)