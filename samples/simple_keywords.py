from alex import Alex

OPERATORS = (("ADD", "+"), ("SUB", "-"), ("EQ", "="))
REGEXPS = (("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"), ("NUM", '^["0123456789"]*'))
KEYWORDS = ['if', 'then']
lexer = Alex(operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS)
lexer.scan('if x = 2 then y = 3')

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)