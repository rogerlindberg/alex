# Installation

This guide explains how to install Alex, verify that it works correctly, and optionally install it from source for development purposes.

---

## Requirements

- Python 3.11 or later  
- A standard Python environment (virtual environments recommended)  
- No additional dependencies — Alex is lightweight and self‑contained

Alex runs on all major platforms: Linux, macOS, and Windows.

---

## Installing via pip

The easiest way to install Alex is from PyPI:

    pip install alex

---

## Upgrade

To upgrader to latest version

    pip install --upgrade alex

---

## Verifying installation

To confirm that Alex is installed correctly, run:

    import alex
    print(alex.__version__)

You can also perform a minima lexer test:

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

If this prints a list of tokens, your installation is working.

---

## Installing from source

If you want the latest development version or plan to contribute:

    git clone https://github.com/rogerlindberg/alex.git
    cd alex
    pip install -e .

This installs Alex in editable mode, allowing you to modify the 
source code and immediately test changes

---

## Uninstalling

To remove Alex from your environment:

    pip uninstall alex

---

## Troubleshooting

### Common issues:

- **Python version mismatch**<br>
Ensure you are running Python 3.11 or later.

- **Virtual environment not activated**<br>
If installation appears successful but import alex fails, verify that your virtual environment is active.
 
- **Old version still installed**<br>
Use pip install --upgrade alex to ensure you have the latest release.

If problems persist, consider reinstalling:

    pip uninstall alex
    pip install alex
