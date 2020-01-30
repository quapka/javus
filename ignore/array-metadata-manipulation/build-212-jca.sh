#!/bin/bash

# build for 212
javacard_framework="$HOME/projects/fi/thesis/ext/jc212_kit/lib/api21.jar:"
src="$1"
echo "Compiling into *.class files.."
# source https://stackoverflow.com/a/35470243/2377489
javac\
    -g\
    -source 1.1\
    -target 1.1\
    -cp "$javacard_framework"\
    "$src"

converter="$HOME/projects/fi/thesis/ext/jc212_kit/lib/converter.jar"
export_path="$HOME/projects/fi/thesis/ext/jc212_kit/api_export_files"
AID="0xA0:0x00:0x00:0x00:0xAA:0x00:0x01"
version="1.0"
echo "Converting into *.cap files.."
java -jar "$converter" -classdir src -out JCA -exportpath "$export_path" com.type_confusion "$AID" "$version"
