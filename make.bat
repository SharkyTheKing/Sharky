@echo off

if [%1] == [] goto help

REM This allows us to expand variables at execution
setlocal ENABLEDELAYEDEXPANSION

goto %1

:reformat
isort --atomic --line-length 99 --use-parentheses .
black -l 99 .
exit /B %ERRORLEVEL%

:stylecheck
isort --atomic --check --line-length 99 --use-parentheses .
black --check -l 99 .
exit /B %ERRORLEVEL%

:stylediff
isort --atomic --check --diff --line-length 99 --use-parentheses .
black --check --diff -l 99 .
exit /B %ERRORLEVEL%

:help
echo Usage:
echo   make ^<command^>
echo.
echo Commands:
echo   reformat                   Reformat all .py files being tracked by git.
echo   stylecheck                 Check which tracked .py files need reformatting.
