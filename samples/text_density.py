"""
Calculate the density of a text

The density is calculated as:

               all-characters  -  spaces
    density =  ---------------------------
                    all-characters

The density will be 1.0 if there are no spaces in the text, and it
will be 0.0 if there are spaces only.
"""

import os
import alex


col_width = 36


def calc_density(text, verbose=False):
    """
    Define an operator SPACE that matches a space character.

    The default skip_chars include the space character sp we have
    to define a new skip_chars string.

    All characters found except the space character are skipped,
    which means they don't generate any tokens.

    The number of tokens found equals the number of spaces in the text.
    """
    operators = (("SPACE", " "),)
    lexer = alex.Alex(
        operators=operators, skip_unrecognized_chars=True, skip_chars="\r\n\t"
    )
    lexer.scan(text)
    if verbose:
        print(f"Nbr of tokens: {len(lexer.tokens)}")
        for token in lexer.tokens:
            print(token)
    return (lexer.nbr_of_bytes - len(lexer.tokens)) / lexer.nbr_of_bytes


def calc_density_for_text_with_no_spaces():
    rv = calc_density("xxxx")
    assert rv == 1.0
    print(f"{'Density for text with no spaces':{col_width}}: {rv:.2}")


def calc_density_for_text_with_spaces_only():
    rv = calc_density("    ")
    assert rv == 0.0
    print(f"{'Density for text with spaces only':{col_width}}: {rv:.2}")


def calc_density_for_docstring():
    rv = calc_density(__doc__)
    print(f"{'Density of Doc-string in this file':{col_width}}: {rv:.2}")


def calc_density_for_alex_code():
    path = os.path.join("..", "alex", "__init__.py")
    _calc_file_density(path, "Density of Alex code")


def calc_density_for_mkdocs_main_code():
    path = os.path.join("..", ".venv", "Lib", "site-packages", "mkdocs", "__main__.py")
    _calc_file_density(path, "Density of mkdocs main code")


def _calc_file_density(filename, report_text):
    with open(filename) as fp:
        rv = calc_density(fp.read())
        print(f"{report_text:{col_width}}: {rv:.2}")


if __name__ == "__main__":
    calc_density_for_text_with_no_spaces()
    calc_density_for_text_with_spaces_only()
    calc_density_for_docstring()
    calc_density_for_alex_code()
    calc_density_for_mkdocs_main_code()
