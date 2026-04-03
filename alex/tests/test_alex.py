import alex


def test_alex():
    """
    >>> alex = alex.Alex()

    >>> alex._msg_prefix('obj', 'y', 'z')
    "obj (y, 'z'):"

    >>> alex._re_msg_prefix('y', 'z')
    "Regexp (y, 'z'):"

    >>> alex._op_msg_prefix('y', 'z')
    "Operator (y, 'z'):"
    """

def test_valid_operators():
    """
    ----(The happy case)----

    >>> lexer = alex.Alex()
    >>> operators = [('ADD', '+'), ('SUB', '-')]
    >>> lexer._validate_operators(operators)
    >>> '+' in lexer.used_token_lexemes
    True
    >>> '-' in lexer.used_token_lexemes
    True
    >>> 'ADD' in lexer.used_token_keys
    True
    >>> 'SUB' in lexer.used_token_keys
    True

    ----(The duplicate key case)----

    >>> lexer = alex.Alex()
    >>> operators = [('ADD', '+'), ('ADD', '-')]
    >>> lexer._validate_operators(operators)
    Traceback (most recent call last):
    ...
    alex.AlexDefinitionError: Operator (ADD, '-'): Key 'ADD' already in use!

    ----(The duplicate value case)----

    >>> lexer = alex.Alex()
    >>> operators = [('ADD', '+'), ('SUB', '+')]
    >>> lexer._validate_operators(operators)
    Traceback (most recent call last):
    ...
    alex.AlexDefinitionError: Operator (SUB, '+'): Value '+' already in use!

    ----(The missing value case)----

    >>> lexer = alex.Alex()
    >>> operators = [('ADD', '+'), ('SUB', '')]
    >>> lexer._validate_operators(operators)
    Traceback (most recent call last):
    ...
    alex.AlexDefinitionError: Operator (SUB, ''): No value given!

    >>> lexer = alex.Alex()
    >>> operators = [('ADD', '+'), ('SUB', None)]
    >>> lexer._validate_operators(operators)
    Traceback (most recent call last):
    ...
    alex.AlexDefinitionError: Operator (SUB, 'None'): No value given!
    """