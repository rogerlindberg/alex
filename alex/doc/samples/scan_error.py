import alex

OPERATORS = (
    ("EQ", "="),
)

REGEXPS = (
    ("ID", f"^[a-zA-Z_]*"),
    ("NUM", '^["0123456789"]*'),
)

lexer = alex.Alex(
    operators=OPERATORS,
    regexps=REGEXPS)

try:
    lexer.scan('x = 1 + 1 + 3')
except alex.AlexScanError as ex:
    print('----(Error report)----------')
    print(ex)
    print()

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)
