"""
Display the version of the alex-lexer package.
"""

import alex


def report_version():
    print(f"alex-lexer version: {alex.version}")


if __name__ == "__main__":
    report_version()
