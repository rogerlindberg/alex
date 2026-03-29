    """
    Determine the nesting level of each function in the input text by analyzing
    indentation.
    
    Example:
        Given this file as input, the expected output is:
    
            Nesting levels for functions:
            Levels Function
            ------ -------------------------------------
               1   main
               2   scan
               4   measure_nesting
               2   print_report
    """
    
    import alex
    
    
    OPERATORS = (
        ("PLUS", "+"),
        ("MINUS", "-"),
        ("MUL", "*"),
        ("DIV", "/"),
        ("DOT", "."),
        ("COMMA", ","),
        ("COLON", ":"),
        ("SEMI", ";"),
        ("AT", "@"),
        ("MOD", "%"),
        ("EQ", "="),
        ("GT", ">"),
        ("LT", "<"),
        ("LP", "("),
        ("RP", ")"),
        ("LBR", "["),
        ("RBR", "]"),
        ("LCBR", "{"),
        ("RCBR", "}"),
        ("OR", "|"),
        ("XOR", "^"),
        ("NOT", "~"),
        ("AND", "&"),
        ("ADDEQ", "+="),
        ("SUBEQ", "-="),
        ("MULEQ", "*="),
        ("DIVEQ", "/="),
        ("IDIVEQ", "//="),
        ("MODEQ", "%="),
        ("LSHIFT", "<<"),
        ("RSHIFT", ">>"),
        ("IDIV", "//"),
        ("EXP", "**"),
        ("GE", ">="),
        ("LE", "<="),
        ("TYPE", "->"),
        ("NEQ", "!="),
        ("EQEQ", "=="),
        ("OREQ", "|="),
        ("XOREQ", "^="),
        ("ANDEQ", "&="),
        ("WALRUS", ":="),
        ("EXPEQ", "**="),
        ("LSHIFTEQ", "<<="),
        ("RSHIFTEQ", ">>="),
    )
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
    ]
    
    
    class Const:
        START_STATE = 0
        IN_FUNCTION_DEF = 1
        INDENT_COUNTING = 2
        DEF = "def"
        INDENT = "INDENT"
    
    
    def main():
        lexer = scan()
        functions_nesting_levels = measure_nesting(lexer)
        print_report(functions_nesting_levels)
    
    
    def scan():
        lexer = alex.Alex(
            operators=OPERATORS,
            regexps=REGEXPS,
            keywords=KEYWORDS,
            scan_python_indents=True,
        )
        lexer.scan_file("python_function_complexity.py")
        return lexer
    
    
    def measure_nesting(lexer):
        functions_nesting_levels = {}
        state = Const.START_STATE
        current_function_name = None
        for token in lexer.tokens:
            if state == Const.START_STATE:
                if token.lexeme == Const.DEF:
                    state = Const.IN_FUNCTION_DEF
            elif state == Const.IN_FUNCTION_DEF:
                current_function_name = token.lexeme
                functions_nesting_levels[current_function_name] = set()
                state = Const.INDENT_COUNTING
            elif state == Const.INDENT_COUNTING:
                if token.name == Const.INDENT:
                    functions_nesting_levels[current_function_name].add(token.lexeme)
                elif token.lexeme == Const.DEF:
                    state = 1
        return functions_nesting_levels
    
    
    def print_report(nestings):
        print("Nesting levels for functions:")
        print("Levels Function")
        print("------ -------------------------------------")
        for key in nestings:
            print(f"{len(nestings[key]):4}   {key}")
    
    
    if __name__ == "__main__":
        main()
