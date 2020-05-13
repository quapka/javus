@echo off

call ..\config.bat

set javac=%java7dir%\bin\javac.exe

call %javac% *.java

