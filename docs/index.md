# Alex — A Lexical Analysis Toolkit for Python

Alex is a lexical analyzer tool. It reads an input string and 
converts it into a list of `Token` objects.  
Each `Token` contains:

- a name (token type)
- the lexeme (the exact matched text)
- the position in the input where it was found

A *lexeme* is a sequence of input characters that together form a single token.

Alex provides a clean, predictable, and idiomatic Python API for 
building lexers that are easy to understand, test, and extend.

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


