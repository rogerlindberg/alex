from alex import Alex

text = "    text = self._read_file(path)\n    self.scan(text)"

REGEXPS = (("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"),)
lexer = Alex(regexps=REGEXPS, skip_unrecognized_chars=True, scan_python_indents=True)
lexer.scan(text)

print('----(Tokens found)----------')
for token in lexer.tokens:
    print(token)
