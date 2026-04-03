class Const:
    DEF = "def"


class FuncNode:
    def __init__(self, def_token=None, name_token=None):
        if def_token:
            self.name = name_token.lexeme
            self.tokens = [def_token, name_token]
        self.funcs = []

    def __repr__(self):
        return f"Name:{self.name} NbrOfTokens: {len(self.tokens)} NbrOfFuncs: {len(self.funcs)}"

    def append_token(self, token):
        self.tokens.append(token)

    def append_func_node(self, func_node):
        self.funcs.append(func_node)

    def print_node(self, indent):
        print(f'{" " * indent}{self}')
        print()
        print(f'{" " * indent}----(Tokens)----')
        for token in self.tokens:
            print(f'{" " * indent}{token}')
        print()
        if len(self.funcs) > 0:
            print(f'{" " * indent}----(Functions)----')
            for node in self.funcs:
                node.print_node(indent + 4)


def create_python_function_tree(gen):
    node = FuncNode()
    try:
        token = gen.__next__()
        while True:
            if token.lexeme == Const.DEF:
                token = _parse_function(gen, token, node)
                if token is None:
                    return nodes(node.funcs)
                continue
            else:
                pass
            token = gen.__next__()
    except StopIteration:
        return nodes(node.funcs)


def nodes(func_nodes):
    for node in func_nodes:
        yield node
        nodes(node)


def _parse_function(gen, def_token, node):
    try:
        col_nbr = def_token.col_nbr
        token = gen.__next__()  # Function name token
        func_node = FuncNode(def_token, token)
        node.append_func_node(func_node)
        token = gen.__next__()
        while token.col_nbr > col_nbr:
            if token.lexeme == Const.DEF:
                token = _parse_function(gen, token, func_node)
                if token and token.lexeme == Const.DEF:
                    continue
                func_node.append_token(token)
            else:
                func_node.append_token(token)
            token = gen.__next__()
        return token
    except StopIteration:
        pass
