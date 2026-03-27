from alex import Alex

text = "text = self._read_file(path)\nself.scan(text)"

REGEXPS = (("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"),)
lexer = Alex(regexps=REGEXPS, treat_unrecognized_chars_as_an_operator=True)
lexer.scan(text)

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)