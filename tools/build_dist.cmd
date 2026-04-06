for %%i in ("%CD%") do set CURRENT_DIR=%%~nxi

IF /I "%CURRENT_DIR%"=="tools" (
    cd ..
)

rmdir /S /Q site
rmdir /S /Q dist
rmdir /S /Q alex_lexer.egg-info

python -m build

popd
