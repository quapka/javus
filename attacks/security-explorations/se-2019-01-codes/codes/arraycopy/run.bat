@echo off
 
call ..\config.bat

set apdutool=%jcdir%\bin\apdutool.bat

call "%apdutool%" script\test.scr
