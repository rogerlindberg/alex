@echo off

for %%i in ("%CD%") do set CURRENT_DIR=%%~nxi

IF /I "%CURRENT_DIR%"=="tools" (
    cd ..
)

twine upload --verbose --repository pypi dist/*
