#!/bin/bash

# compile
sdks_dir="submodules/oracle_javacard_sdks"
classdir="classes-221"
build_dir="build-221"

echo "Compiling.."
javac -g -source 1.2 -target 1.2 -cp "$sdks_dir"/jc221_kit/lib/javacardframework.jar src/SEApplet.java src/Cast.java -d "$classdir"



# call %javac% -classpath %classpath% -d classes src\*.java
converter="$sdks_dir/jc221_kit/bin/converter"
exportpath="$sdks_dir/jc221_kit/api_export_files:$build_dir"

echo "Converting.."
"$converter" -classdir "$classdir" -i -d "$build_dir" -out EXP CAP JCA -exportpath "$exportpath" com.se.vulns 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x2 1.0
"$converter" -classdir "$classdir" -i -d "$build_dir" -out EXP CAP JCA -exportpath "$exportpath" -applet 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1:0x1 com.se.applets.SEApplet com.se.applets 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1 1.0

