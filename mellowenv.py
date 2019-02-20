class Environment:
    def __init__(self):
        self.variables = dict()
        self.functions = dict()
        self.arguments = dict()
        self.args = [[],[]]
        self.imports = dict()
        self.decorators = dict()
