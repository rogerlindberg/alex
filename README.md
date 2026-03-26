# alex

**alex** is a lexical analyzer tool.

It reads and converts the input to a
list of **Token** objects. 

A **Token** contains a name end the lexeme as well
as the position in the input where it was found. (A lexeme is a sequence
of input characters that comprise a single token)

---

## 🚀 Installation

Installera direkt från PyPI:

    pip install alex

or in development mode:

    pip install -e .

## Usage

Instantiate the class **Alex** and call one of the functions

- scan(text)
- scan_file(path)
- generate(text)
- generate_file(path)

The scan functions returns a list of Tokens while the
generate functions creates a generator that returns one 
Token at a time.

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
contains the lexeme of the lexcial token.

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

## Definition error example - def_error.py

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


## Scan error example - scan_error.py

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
        skip_unrecognized_chars=True)

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

In the definitions of reqular expressions
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

will be converted to a set.

    {'if', 'then'}
    

## The Token class

A Token class object has four attributes.

- name
- lexeme
- line_nbr
- col_nbr

and a __repr__() function that returns these attributes as one string.

