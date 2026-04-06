import os
from collections import Counter
import alex


REGEXPS = (("DEF", r"^def\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*(?:->\s*[^:]+)?\s*:"),)

lexer = alex.Alex(regexps=REGEXPS, skip_unrecognized_chars=True)

path = os.path.join('..', 'alex', '__init__.py')
lexer.scan_file(path)


print("----(Tokens found)----------")
for token in lexer.tokens:
    print(token)
print()

print("----(Function names only)----------")
counter = Counter()
for token in lexer.tokens:
    name = token.lexeme.split("(")[0].split()[1]
    counter.update([name])
    print(name)
print()

print("----(Duplicated names)----------")
print([item[0] for item in counter.items() if item[1] > 1])
