@echo off

IF EXIST "..\alex\tests\run_tests.py" (
  pushd ..\alex\tests
) ELSE (
  pushd alex\tests
)

python run_tests.py
popd
