from rply.token import BaseBox
import time
import importlib
import inspect


class Number(BaseBox):
    def __init__(self, value):
        self.value = value

    async def eval(self, env):
        return int(self.value)

class Boolean(BaseBox):
    def __init__(self, value):
        self.value = bool(value)

    async def eval(self, env):
        return self.value

class BinaryOp(BaseBox):
    def __init__(self, left, right):
        self.left = left
        self.right = right


class Sum(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) + await self.right.eval(env)

class Sub(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) - await self.right.eval(env)

class Mul(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) * await self.right.eval(env)

class Div(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) / await self.right.eval(env)

class Print:
    def __init__(self, value):
        self.value = value

    async def eval(self, env):
        x = await self.value.eval(env)
        print(x)

class String(BaseBox):
    def __init__(self, value):
        self.value = value

    async def eval(self, env):
        return self.value.strip('"\'')

class Variable(BaseBox):
    def __init__(self, name):
        self.name = str(name)
        self.value = None

    async def eval(self, env):
        kwargs = dict()
        for i in range(len(env.args[1])):
            kwargs.update({env.args[0][i]:env.args[1][i]})
        if env.variables.get(self.name):
            self.value = env.variables[self.name]
            return self.value
        elif env.arguments.get(self.name):
            self.value = await env.arguments[self.name].eval(env)
            return self.value
        elif kwargs.get(self.name):
            self.value = await kwargs[self.name].eval(env)
            return self.value
        raise NameError("Not yet defined")

class Assignment(BinaryOp):
    async def eval(self, env):
        if isinstance(self.left,Variable):
            if not env.variables.get(self.left.name):
                env.variables[self.left.name] = await self.right.eval(env)
                return self.right
        else:
            raise NameError("Cannot assign to this")

class Program(BaseBox): 
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)
        self.run = False
    
    def add_statement(self, statement):
        self.statements.insert(0,statement)
        
    async def eval(self, env):
        result = None
        for statement in self.statements:
            result = await statement.eval(env)
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
        
    async def eval(self, env): 
        if await self.condition.eval(env): 
            return await self.body.eval(env)
        elif self.elif_condition and self.elif_body and self.else_body:
            if await self.elif_condition.eval(env):
                return await self.elif_body.eval(env)
            else:
                if self.else_body:
                    return await self.else_body.eval(env)
        elif self.elif_condition and self.elif_body:
            if await self.elif_condition.eval(env):
                return await self.elif_body.eval(env)
        else:
            if self.else_body:
                return self.else_body.eval(env)
        return None

class Equal(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) == await self.right.eval(env)

class NotEqual(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) != await self.right.eval(env)
        
class GreaterThan(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) > await self.right.eval(env)

class LessThan(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) < await self.right.eval(env)

class GreaterThanEqual(BinaryOp):
    async def eval(self, env):
        return await self.left.eval(env) >= await self.right.eval(env)

class LessThanEqual(BinaryOp):
    async def eval(self, env):
        return await  self.left.eval(env) <= await self.right.eval(env)

class Function(BaseBox):
    def __init__(self, name, args=None):
        self.name = name
        self.value = None
        self.args = args

    async def eval(self, env):
        if env.functions.get(self.name):
            needed = env.functions[self.name][1]
            have = self.args.statements if self.args else []
            env.arguments = dict()
            for i in range(len(needed)):
                try:
                    env.arguments.update({needed[i].name:have[i]})
                except IndexError:
                    raise TypeError(self.name + "() missing required arguments.")
            self.value = await env.functions[self.name][0].eval(env)
            env.arguments = dict()
            return self.value
        raise NameError("Not yet defined")

class AssignmentFunction:
    def __init__(self, name, function, args):
        self.name = name
        self.function = function
        if args:
            self.args = args.statements
        else:
            self.args = None

    async def eval(self, env):
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

    async def eval(self, env):
        
        if len(self.values) == 0:            
            for statement in self.statements:
                self.values.append(await statement.eval(env))
        return self

class Block(BaseBox):
    
    def __init__(self, statement):
        self.statements = []
        self.statements.append(statement)
    
    def add_statement(self, statement):
        self.statements.insert(0,statement)
    
    def get_statements(self):
        return self.statements
    
    async def eval(self, env):
        result = None
        for statement in self.statements:
            result = await statement.eval(env)
        return result

class Sleep:
    def __init__(self, time):
        self.time = time
    
    async def eval(self, env):
        time.sleep(self.time)

class Open:
    def __init__(self, filepath):
        self.filepath = filepath
    
    async def eval(self, env):
        return open(self.filepath.strip("'\""))

class Read:
    def __init__(self, file):
        self.file = file
        self.value = None
    
    async def eval(self, env):
        if self.value:
            return self.value
        elif isinstance(self.file, Open):
            x = await self.file.eval(env)
            self.value = x.read()
            return self.value
        elif isinstance(self.file, Variable):
            x = await self.file.eval(env)
            self.value = x.read()
            return self.value
        else:
            self.value = self.file.read()
            return self.value

class Return:
    def __init__(self, expression):
        self.exp = expression
    
    async def eval(self, env):
        return await self.exp.eval(env)

class Import:
    def __init__(self, name, module):
        self.name = name
        self.module = module
    
    async def eval(self, env):
        if self.module:
            name = "." + self.name
            imported = importlib.import_module(name, self.module)
            env.imports.update({self.name: dict()})
            for m in dir(imported):
                f = getattr(imported, m)
                env.imports[self.name].update({m : f})
            return imported 
        else:
            imported = importlib.import_module(self.name)
            env.imports.update({self.name: dict()})
            for m in dir(imported):
                f = getattr(imported, m)
                env.imports[self.name].update({m : f})
            return imported

class ImportedFunction:
    def __init__(self, module, function, args=None, kwargs = None):
        self.name = function
        self.module = module
        self.function = function
        if args:
            self.args = args.statements
        else:
            self.args = None
        if kwargs:
            self.kwargs = kwargs.statements
        else:
            self.kwargs = None
    
    async def eval(self, env):
        if env.variables.get(self.module):
            m = env.variables[self.module]
            if getattr(m, self.function):
                f = getattr(m,self.function)
                if self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    args = [await arg.eval(env) for arg in self.args]
                    return f(*args, **kwargs)
                elif self.args and not self.kwargs:
                    args = [await arg.eval(env) for arg in self.args]
                    return f(*args)
                elif not self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    return f(**kwargs)
                else:
                    return f()
        elif env.imports.get(self.module):
            m = env.imports[self.module]
            if m.get(self.function):
                f = m[self.function]
                if self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    args = [await arg.eval(env) for arg in self.args]
                    return f(*args, **kwargs)
                elif self.args and not self.kwargs:
                    args = [await arg.eval(env) for arg in self.args]
                    return f(*args)
                elif not self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    return f(**kwargs)
                else:
                    return f()
        raise NameError("Not yet Defined")

class InnerDict(BaseBox):
    def __init__(self, statements = None):
        self.data = {}
        self.values = {}
        self.statements = {}
        if statements:
            self.statements = statements
            self.data = statements

    def update(self, key, val):
        self.data[key] = val

class Dict(BaseBox):
    def __init__(self, inner):
        self.data = inner.data
        self.statements = inner.statements
        self.values = list()
    
    def update(self, key, val):
        self.data[key] = val
    
    async def eval(self, env):
        if len(self.values) == 0:            
            for statement in self.statements:
                self.values.append(await statement.eval(env))
        data = {}
        for k in self.data:
            data.update({await k.eval(env) : await self.data[k].eval(env)})
        return data

class GetAttr:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    
    async def eval(self, env):
        if not isinstance(self.left, Variable):
            if env.variables.get(self.left):
                return getattr(env.variables.get(self.left), self.right)
            elif env.imports.get(self.left):
                return env.imports.get(self.left).get(self.right)
        else:
            if env.variables.get(await self.left.eval(env)):
                return env.imports.get(await self.left.eval(env)).get(self.right)
            elif env.variables.get(await self.left.eval(env)):
                return getattr(env.variables.get(await self.left.eval(env)), self.right)
        raise AttributeError(str(type(self.left)) + " has no attribute " + self.right)

class Await(BaseBox):
    def __init__(self, function):
        if isinstance(function, Function):
            raise TypeError("Non async functions can't be used in await expressions")
        self.kwargs = function.kwargs
        self.module = function.module
        self.args = function.args
        self.function = function.function

    async def eval(self, env):
        if env.imports.get(self.module):
            m = env.imports[self.module]
            if m.get(self.function):
                f = m[self.function]
                if self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    args = [await arg.eval(env) for arg in self.args]
                    return await f(*args, **kwargs)
                elif self.args and not self.kwargs:
                    args = [await arg.eval(env) for arg in self.args]
                    return await f(*args)
                elif not self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    return await f(**kwargs)
                else:
                    return await f()
        elif env.variables.get(self.module):
            v = env.variables[self.module]
            try:
                f = getattr(v, self.function)
                if self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    args = [await arg.eval(env) for arg in self.args]
                    return await f(*args, **kwargs)
                elif self.args and not self.kwargs:
                    args = [await arg.eval(env) for arg in self.args]
                    return await f(*args)
                elif not self.args and self.kwargs:
                    kwargs = {}
                    for k in self.kwargs:
                        kwargs.update({k : await self.kwargs[k].eval(env)})
                    return await f(**kwargs)
                else:
                    return await f()
            except AttributeError:
                raise NameError("This variable does not have that function")
        raise NameError("Not yet Defined")
        
class DecoratedFunction:
    def __init__(self, first, second, function, paren, args, kwargs):
        self.first = first
        self.second = second
        self.function = function
        self.paren = paren
        if args:
            self.args = args.statements
        else:
            self.args = None
        if kwargs:
            self.kwargs = kwargs.statements
        else:
            self.kwargs = None
    
    async def eval(self, env):
        def rename(newname):
            def decorator(f):
                f.__name__ = newname
                return f
            return decorator
        if env.variables.get(self.first):
            f = env.variables.get(self.first)
            d = getattr(f, self.second)
            kwargs = {}
            if self.kwargs:
                for k in self.kwargs:
                    kwargs.update({k : await self.kwargs[k].eval(env)})
            args = []
            if self.args:
                args = [await arg.eval(env) for arg in self.args]
            if self.paren:
                @rename(self.function.name)
                @d(*args, **kwargs)
                async def call(*fargs):
                    for i in range(len(list(fargs))):
                        env.variables.update({self.function.args[i].name:fargs[i]})
                    await self.function.function.eval(env)
            else:
                @rename(self.function.name)
                async def call(*fargs):
                    for i in range(len(list(fargs))):
                        env.variables.update({self.function.args[i].name:fargs[i]})
                    await self.function.function.eval(env)
                call = d(call)
            env.decorators[self.function.name] = call
            return call
        elif env.imports.get(self.first):
            f = env.variables.get(self.first)
            d = getattr(f, self.second)
            kwargs = {}
            if self.kwargs:
                for k in self.kwargs:
                    kwargs.update({k : await self.kwargs[k].eval(env)})
            args = []
            if self.args:
                args = [await arg.eval(env) for arg in self.args]
            if self.paren:
                @rename(self.function.name)
                @d(*args, **kwargs)
                async def call(*fargs):
                    for i in range(len(list(fargs))):
                        env.variables.update({self.function.args[i].name:fargs[i]})
                    await self.function.function.eval(env)
            else:
                @rename(self.function.name)
                async def call(*fargs):
                    for i in range(len(list(fargs))):
                        env.variables.update({self.function.args[i].name:fargs[i]})
                    await self.function.function.eval(env)
                call = d(call)
            env.decorators[self.function.name] = call
            return call
        raise NameError("Variable is not defined")