#!/bin/bash

# build for 222
javacard_framework="$HOME/projects/fi/thesis/ext/jc222_kit/lib/javacardframework.jar:"
src="$1"
echo "Compiling into *.class files.."
# source https://stackoverflow.com/a/35470243/2377489
javac\
    -g\
    -source 1.5\
    -target 1.5\
    -cp "$javacard_framework"\
    "$src"

converter="$HOME/projects/fi/thesis/ext/jc222_kit/bin/converter"
export_path="$HOME/projects/fi/thesis/ext/jc222_kit/api_export_files"
# AID="0xA0:0x00:0x00:0x00:0xAA:0x00:0x01"
AID="0xA0:0x00:0x00:0x00:0xAA:0x55:0x01"
version="1.0"
echo "Converting into *.cap files.."
"$converter" -noverify -classdir src -out JCA -exportpath "$export_path" com.type_confusion "$AID" "$version"
