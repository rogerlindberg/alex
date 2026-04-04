@echo off

REM Hämta katalogen där skriptet ligger
set SCRIPT_DIR=%~dp0

REM Ta bort avslutande backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Hämta skriptets föräldrakatalog (där alex ligger)
for %%A in ("%SCRIPT_DIR%\..") do set PROJECT_DIR=%%~fA

REM Om vi står i projektroten (alex)
IF /I "%CD%"=="%PROJECT_DIR%" (
    pushd tests
) ELSE (
    pushd "%PROJECT_DIR%\tests"
)
echo %CD%
python run_tests.py
popd
