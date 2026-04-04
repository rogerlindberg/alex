# alex

**alex** is a lexical analyzer tool.

It reads an input string and converts it into a list of **Token** 
objects.  

A **Token** contains:

- a name (token type)
- the lexeme (the exact matched text)
- the position in the input where it was found

A **lexeme** is a sequence of input characters that together form a 
single token.

**alex** provides a clean, predictable, and idiomatic Python API for 
building lexers that are easy to understand, test, and extend.

With the right composition of input rules, it can scan any text file 
and extract the tokens you define.

---

## Key Features

- **Straightforward token model**  
  Every token carries its type, matched text, and position.

- **Composable rule system**  
  Define patterns using regular expressions and map them to token classes.

- **Deterministic lexer pipeline**  
  Input is processed left‑to‑right with clear, explicit behavior.

- **Domain‑specific exceptions**  
  Errors are raised with meaningful context to simplify debugging.

- **Minimal dependencies**  
  Lightweight and suitable for both small utilities and large applications.

---


## 🚀 Installation

Install directly from PyPI:

    pip install alex-lexer


## Usage

Instantiate the class **Alex** and call one of the functions

- scan(text)
- scan_file(path)
- generate(text)
- generate_file(path)

The scan functions returns a list of Tokens while the
generate functions creates a generator that returns one 
**Token** at a time.

When instantiating the class **Alex** you
must provide definitions of the tokens
that can appear in your input text.

The definitions to be defined are:

- operators (A list/tuple of tuples)
- regexps   (A list/tuple of tuples)
- keywords (A list of strings)

## Example - simple.py

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

will output the following:

    ----(Tokens found)----------
        1:  1  NUM          1           
        1:  3  ADD          +           
        1:  5  NUM          2           
        1:  7  SUB          -           
        1:  9  NUM          123  

The first column contains the line number and
the second column contains the column number
in witch the lexical token was found.

The third column contains the name of the token
given in the definitions and the last column
contains the lexeme of the token.

## Example - keywords.py

    import alex
    
    OPERATORS = (
        ("EQ", "="),
        ("EQEQ", "=="),
    )
    REGEXPS = (
        ("ID", f"^[a-zA-Z_]*"),
        ("NUM", '^["0123456789"]*'),
    )
    KEYWORDS = [
        'if',
        'then',
    ]
    
    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        keywords=KEYWORDS)
    
    lexer.scan('''if foo == bar 
    then x = 17''')
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

In this example we have added a KEYWORDS definition
and added a REGEXP to find identifiers.

The output is:

    ----(Tokens found)----------
        1:  1  KEYWORD      if          
        1:  4  ID           foo         
        1:  8  EQEQ         ==          
        1: 11  ID           bar         
        2:  1  KEYWORD      then        
        2:  6  ID           x           
        2:  8  EQ           =           
        2: 10  NUM          17 

## Error handling

When an error occurs one of the following exceptions is issued.

- AlexDefinitionError,
- AlexScanError,

**AlexDefinitionError** is raised when there is something wrong
with your definitions and **AlexScanError** is raised when a
problem is detected during the scanning of the input text.

## AlexDefinitionError example - def_error.py

    import alex
    
    
    OPERATORS = (
        ("ADD", "+"),
        ("ADD", "-"),
    )
    
    REGEXPS = (
        ("NUM", '^["0123456789"]*'),
    )
    
    
    try:
        lexer = alex.Alex(
            operators=OPERATORS,
            regexps=REGEXPS)
        lexer.scan('1 + 2 - 123')
    except alex.AlexDefinitionError as ex:
        print('----(Error report)----------')
        print(ex)
    
The output is
    
    ----(Error report)----------
    Operator (ADD, '-'): Key 'ADD' already in use!


## AlexScanError example - scan_error.py

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

The output is:

    ----(Error report)----------
    Unrecognized char '+' ordinal 43
    Following 10 characters are:  1 + 3
    Last scanned Token:     1:  5  NUM          1           
    
    ----(Tokens found)----------
        1:  1  ID           x           
        1:  3  EQ           =           
        1:  5  NUM          1           

If you don't want an exception you can define
what shall happen when an unrecognized character
is found.

- skip_unrecognized_chars
- treat_unrecognized_chars_as_an_operator
- define a set of skip characters

    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        skip_unrecognized_chars=True)

Then the output will be:

    ----(Tokens found)----------
        1:  1  ID           x           
        1:  3  EQ           =           
        1:  5  NUM          1           
        1:  8  NUM          1           
        1: 11  NUM          3   

or you can do

    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        treat_unrecognized_chars_as_an_operator=True)

and the output will be:

    ----(Tokens found)----------
        1:  1  ID           x           
        1:  3  EQ           =           
        1:  5  NUM          1           
        1:  7  UNRECOGNIZED-CHAR +           
        1:  9  NUM          1           
        1: 11  UNRECOGNIZED-CHAR +           
        1: 13  NUM          3    

or define a set of characters to skip.
By default, space and tab are defined as
characters to skip, but you can define
your own set.

    lexer = alex.Alex(
        operators=OPERATORS,
        regexps=REGEXPS,
        skip_chars=' \t+')

And the output will be:

    ----(Tokens found)----------
        1:  1  ID           x           
        1:  3  EQ           =           
        1:  5  NUM          1           
        1:  9  NUM          1           
        1: 13  NUM          3 

## Regular expressions

In the definitions of regular expressions
the **^** character must be the first
character in the expression.

    REGEXPS = (
        ("NUM", '^["0123456789"]*'),
    )

## Keywords lists

Duplicate definitions of the same keywords
will be silently removed.

    KEYWORDS = [
        'if',
        'if',
        'then',
    ]

by converting the keywords to a set.

    {'if', 'then'}
    

## The Token class

A **Token** class object has four attributes.

- name
- lexeme
- line_nbr
- col_nbr

and a __repr__() function that returns these attributes as one string.

## Example - scanning python

This example shows how you can get tokens from a python file.
It has been tested, but no garanti given that it works for every case.

It uses the flag

    scan_python_indents=True

to save indent information as a token. 
The lexeme of such a token is the length of the indent.

This only works correct if the indents only consists of spaces and not tabs.

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
    
    lexer = alex.Alex(
        operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS, scan_python_indents=True
    )
    
    lexer.scan_file("test.py")
    
    print("----(Tokens found)----------")
    for token in lexer.tokens:
        print(token)

## Building distribution

To build a distribution that can be uploaded to PyPi, run the
following command:

    tools/build_dist.cmd

In order for this to work the **build** package must be installed.

## Upload distribution to PyPi

In order to upload a new distribution you first have to bump up
the **version number** in **pyproject.toml**. You can't upload
the same version twice.

Thereafter, run the command

    tools/install_pypi.cmd

## Run documentation server locally

To test the documentation web pages you can start a local
server with the command:

    tools/docs_server.cmd


## Upload documentation to Github

The documentation is found at https://rogerlindberg.github.io/alex

To upload new or editied documentation, use the command:

    tools/docs_to_github.cmd

The documentation is created with **mkdocs**, which must be installed.


## Run tests

For testing the package **pytest** must be installed.

All tests are found. in the **tests** directory.

To run all tests:

    python tools/run_tests.cmd

