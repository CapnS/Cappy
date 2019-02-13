from rply.token import BaseBox
from capnenv import Environment

cenv = Environment()
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
        self.value = str(value)

    def eval(self, env):
        return self.value

class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None

    def eval(self, env):
        if env.variables.get(self.name, None) is not None:
            self.value = env.variables[self.name].eval(env)
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
    def __init__(self, name, env):
        self.name = name
        self.value = None
        self.env = env
        print(name)

    def eval(self, env):
        print("CALL")
        if self.env.functions.get(self.name):
            print("CALLED")
            self.value = self.env.functions[self.name]
            return self.value
        raise NameError("Not yet defined")

class AssignmentFunction:
    def __init__(self, func, function, env):
        self.func = func
        self.function = function
        self.env = env

    def eval(self, env):
        if isinstance(self.func, Function):
            print("DEFINED")
            self.env.functions[self.func.name] = self.function
            return self.func
        else:
            raise NameError("Cannot assign to this")

class Call:
    def __init__(self, function, env):
        env.functions.get(function.name).eval(env)