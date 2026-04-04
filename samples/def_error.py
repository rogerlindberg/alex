import alex


OPERATORS = (
    ("ADD", "+"),
    ("ADD", "-"),
)

REGEXPS = (("NUM", '^["0123456789"]*'),)


try:
    lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)
    lexer.scan("1 + 2 - 123")
except alex.AlexDefinitionError as ex:
    print("----(Error report)----------")
    print(ex)
