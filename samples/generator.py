import alex


OPERATORS = (
    ("ADD", "+"),
    ("SUB", "-"),
)

REGEXPS = (("NUM", '^["0123456789"]*'),)


def with_generator():
    lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)

    for token in lexer.generate("1 + 2 - 123"):
        print(token)
        input("Enter for next>")


def with_generator_file():
    lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)

    for token in lexer.generate_file("some_code.txt"):
        print(token)
        input("Enter for next>")


def without_generator():
    lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)
    lexer.scan("1 + 2 - 123")
    for token in lexer.tokens:
        print(token)


with_generator_file()
