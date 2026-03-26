import alex


OPERATORS = (
    ("ADD", "+"),
    ("SUB", "-"),
)

REGEXPS = (
    ("NUM", '^["0123456789"]*'),
)

lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS)

lexer.scan('1 + 2 - 123')

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)
