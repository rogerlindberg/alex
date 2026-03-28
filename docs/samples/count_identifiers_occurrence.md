    """
    Count the number of occurrences of identifiers in the input and print a
    sorted top list to stdout.
    
    In this example, the input is this file and the expected output is:
    
        ----(Counting 5 most common occurrences of identifier names)----------
          3 lexer
          3 token
          2 Counter
          2 alex
          2 REGEXPS
    """
    
    from collections import Counter
    import alex
    
    
    REGEXPS = (
        ("TSTR", r'^f?"""(?:\\.|(?!""").)*?"""|^f?\'\'\'(?:\\.|(?!\'\'\').)*?\'\'\''),
        ("STR", r'^f?"(?:\\.|[^"\\])*"|^f?\'(?:\\.|[^\'\\])*\''),
        ("NUM", '^["0123456789"]*'),
        ("REM", "^#[^\n]*"),
        ("ID", f"^[a-zA-Z_0-9]*"),
    )
    KEYWORDS = [
        "False",
        "None",
        "True",
        "and",
        "as",
        "assert",
        "async",
        "await",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
        "self",
        "dict",
        "set",
        "string",
        "isinstance",
        "args",
        "kwargs",
        "len",
    ]
    
    
    def main():
        lexer = alex.Alex(regexps=REGEXPS, keywords=KEYWORDS, skip_unrecognized_chars=True)
        scan(lexer)
        print_report(lexer)
    
    
    def scan(lexer):
        lexer.scan_file("count_identifiers_occurrence.py")
    
    
    def print_report(lexer):
        show = 5
        print(
            f"----(Counting {show} most common occurrences of identifier names)----------"
        )
        names = [token.lexeme for token in lexer.tokens if token.name == "ID"]
        counter = Counter(names).most_common(show)
        for name, length in counter:
            print(f"{length:3} {name}")
    
    
    if __name__ == "__main__":
        main()
