import alex


OPERATORS = (
    ("ADD", "+"),
    ("SUB", "-"),
)

REGEXPS = (
    ("NUM", '^["0123456789"]*'),
    ("NUM", '^["0123456789"]*'),
)


def demonstrate():
    try:
        lexer = alex.Alex(operators=OPERATORS, regexps=REGEXPS)
    except alex.AlexDefinitionError as ex:
        print(ex)


if __name__ == "__main__":
    demonstrate()
