@echo off

call ..\config.bat

set java=%java7dir%\bin\java.exe

call %java% Gen %1 %2 %3 %4 %5
