@echo off

rmdir /S /Q site
rmdir /S /Q dist
rmdir /S /Q alex_lexer.egg-info

python -m build
