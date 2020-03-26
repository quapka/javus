@echo off

if "%1" == "" goto buildall

call ..\config.bat

set poc=%1
set genidx=%2
set genarg=%3

set java=%java7dir%\bin\java.exe
set javac=%java7dir%\bin\javac.exe
set converter=%jcdir%\bin\converter.bat
set scriptgen=%jcdir%\bin\scriptgen.bat

set classpath="%jcdir%\lib\api_classic.jar;%jcdir%\lib\api_classic_annotations.jar;%jcdir%\lib\tools.jar;%jcdir%\lib\jctasks.jar;%jcdir%\lib\ant-contrib-1.0b3.jar;."
set exportpath="%jcdir%\api_export_files;build"

set packages=vulns applets

echo *** Compiling source files ***
for %%i in (%packages%) do (
 del classes\com\se\%%i\*.class
 del build\com\se\%%i\javacard\*.exp
 del build\com\se\%%i\javacard\*.cap
 del build\com\se\%%i\javacard\*.jca
)

del script\install1.scr
del script\install2.scr
del script\test.scr

call %javac% -classpath %classpath% -d classes src\*.java

call "%converter%" -classdir classes -i -d build -out EXP CAP JCA -exportpath %exportpath% com.se.vulns 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x2 1.0
call "%converter%" -classdir classes -i -d build -out EXP CAP JCA -exportpath %exportpath% -applet 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1:0x1 com.se.applets.SEApplet com.se.applets 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1 1.0

cd ..\_gen
call build.bat
call run.bat %~dp0\%poc%\build\com\se\vulns\javacard\vulns.cap %~dp0\%poc%\build\com\se\vulns\javacard\vulns.exp %~dp0\%poc%\build\com\se\vulns\javacard\vulns.new.cap %genidx% %genarg%
cd %~dp0\%poc%

call "%scriptgen%" build\com\se\vulns\javacard\vulns.new.cap -o script\install1.scr
call "%scriptgen%" build\com\se\applets\javacard\applets.cap -o script\install2.scr

copy script\powerup.scr script\test.scr
type script\install1.scr >> script\test.scr
type script\install2.scr >> script\test.scr
type test.scr >> script\test.scr
type script\powerdown.scr >> script\test.scr

goto done

:buildall
set pocs=baload_bastore arraycopy staticfield_ref referencelocation swap_x nativemethod arrayops localvars

echo *** Building POCs ***
for %%i in (%pocs%) do (
 cd %%i
 call build.bat
 cd ..
)

:done
