import alex


OPERATORS = (
    ("ADD", "+"),
    ("SUB", "+"),
)

REGEXPS = (
    ("NUM", '^["0123456789"]*'),
)


try:
    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS)
    lexer.scan('1 + 2 + 123')
    for token in lexer.tokens:
        print(token)
except alex.AlexDefinitionError as ex:
    print(ex)


