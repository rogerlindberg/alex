# Usage

This guide shows how to use alex in real code: creating a lexer, 
defining rules, tokenizing input, and handling common scenarios.


## Minimal working example

    from alex import Alex
    
    
    OPERATORS = ( ("ADD", "+"), ("SUB", "-") )
    REGEXPS = ( ("NUM", '^["0123456789"]*'), )
    
    lexer = Alex(operators=OPERATORS, regexps=REGEXPS)
    lexer.scan('1 + 2 - 123')
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

Output:

    ----(Tokens found)----------
        1:  1  NUM          1           
        1:  3  ADD          +           
        1:  5  NUM          2           
        1:  7  SUB          -           
        1:  9  NUM          123     


## Operators

Operators are fixed strings and are defined as a tuple
of tuple items.

Each tuple item has two parts, a **name** and a **lexeme**.
The **lexeme** describes the text to match in the
input text and the **name** is your choice of a unique string.

### Example

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

Operators are sorted by lexeme length in descending order.

This means that the longest operator lexeme are matched first.

Operators are matched before regexps.

## Regular expressions

Regular expressions are also defined as a tuple
of tuple items.

Each tuple item has two parts, a **name** and a **regular expression**.
The **regular expression** describes the text to match in the
input text and the **name** is your choice of a unique string.

### Example

    REGEXPS = (
        ("TSTR", r'^f?"""(?:\\.|(?!""").)*?"""|^f?\'\'\'(?:\\.|(?!\'\'\').)*?\'\'\''),
        ("STR", r'^f?"(?:\\.|[^"\\])*"|^f?\'(?:\\.|[^\'\\])*\''),
        ("NUM", '^["0123456789"]*'),
        ("REM", "^#[^\n]*"),
        ("ID", f"^[a-zA-Z_0-9]*"),
    )

Regular expressions are matched in the order that they have
in the tuple.

The regular expression must start with the ^-character.


## Keywords

If you want to distinguish an identifier from a language keyword,
you can define a list of keywords.

A token for a keyword will be given the name 'KEYWORD'.
That means that no operator definition or regexp definition must
have the name 'KEYWORD'.

### Example

    from alex import Alex
    
    
    OPERATORS = ( ("ADD", "+"), ("SUB", "-"), ("EQ", "=") )
    REGEXPS = ( ("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"), ("NUM", '^["0123456789"]*') )
    KEYWORDS = ['if', 'then']
    lexer = Alex(operators=OPERATORS, regexps=REGEXPS, keywords=KEYWORDS)
    lexer.scan('if x = 2 then y = 3')
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

The output will be:

    ----(Tokens found)----------
        1:  1  KEYWORD      if          <---- KEYWORD
        1:  4  ID           x           <---- ID
        1:  6  EQ           =           
        1:  8  NUM          2           
        1: 10  KEYWORD      then        
        1: 15  ID           y           
        1: 17  EQ           =           
        1: 19  NUM          3

## Processing flags

### skip_unrecognized_chars

This flag kan be used to skip all unrecognized characters
in the input text. The default value is **False**.

I you for example only are interested in finding all
identifier names in an input text and skip all the rest,
you can set skip_unrecognized_chars=True

    from alex import Alex
    
    
    text = "text = self._read_file(path)\nself.scan(text)"

    REGEXPS = ( ("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"),  )
    lexer = Alex(regexps=REGEXPS, skip_unrecognized_chars=True)
    lexer.scan(text)
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

Will output:

    ----(Tokens found)----------
        1:  1  ID           text        
        1:  7  ID           self        
        1: 11  ID           _read_file  
        1: 21  ID           path        
        2:  1  ID           self        
        2:  5  ID           scan        
        2:  9  ID           text       

### treat_unrecognized_chars_as_an_operator

If you want to see all skipped characters in the tokens list
you can set this flag to True. Default value is **False**.


    from alex import Alex
    
    
    text = "text = self._read_file(path)\nself.scan(text)"

    REGEXPS = ( ("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"),  )
    lexer = Alex(regexps=REGEXPS, treat_unrecognized_chars_as_an_operator=True)
    lexer.scan(text)
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

Will output:

    ----(Tokens found)----------
        1:  1  ID           text        
        1:  6  UNRECOGNIZED-CHAR =           
        1:  8  ID           self        
        1: 12  UNRECOGNIZED-CHAR .           
        1: 13  ID           _read_file  
        1: 23  UNRECOGNIZED-CHAR (           
        1: 24  ID           path        
        1: 28  UNRECOGNIZED-CHAR )           
        2:  1  ID           self        
        2:  5  UNRECOGNIZED-CHAR .           
        2:  6  ID           scan        
        2: 10  UNRECOGNIZED-CHAR (           
        2: 11  ID           text        
        2: 15  UNRECOGNIZED-CHAR )              

### scan_python_indents

With this flag set to **True** (default = **False**), you can get
indentation information as an output token.

    from alex import Alex
    
    text = "    text = self._read_file(path)\n    self.scan(text)"
    
    REGEXPS = (("ID", f"^[a-zA-Z_][a-zA-Z_0-9]*"),)
    lexer = Alex(regexps=REGEXPS, skip_unrecognized_chars=True, scan_python_indents=True)
    lexer.scan(text)
    
    print('----(Tokens found)----------')
    for token in lexer.tokens:
        print(token)

Output:

    ----(Tokens found)----------
        1:  1  INDENT       4           
        1:  5  ID           text        
        1: 11  ID           self        
        1: 15  ID           _read_file  
        1: 25  ID           path        
        2:  1  INDENT       4           
        2:  5  ID           self        
        2:  9  ID           scan        
        2: 13  ID           text  

This means that 'INDENT' also is a reserver word like 'KEYWORD'
and cant be used for your own definitions.
