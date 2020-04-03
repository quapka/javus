#!/bin/bash

echo "*** Configure ***"
../config.sh
export javadir="/usr/"
export jcdir="/home/qup/projects/fi/thesis/ext/jc222_kit/"
export jcdir3_5="/home/qup/projects/fi/thesis/ext/jc305u3_kit"
export simdir="/home/qup/projects/fi/thesis/ext/jc222_kit/"

if [ -z "$1" ]; then
    # build all
    # pocs="baload_bastore arraycopy staticfield_ref referencelocation swap_x nativemethod arrayops localvars"
    pocs="baload_bastore"

    echo "*** Building POCs ***"
    for i in "$pocs";
    do
         pushd "$i"
        ./build.sh
         popd
     done
else
    export poc=$1
    export genidx=$2
    export genarg=$3

    export java="$javadir/bin/java"
    export javac="$javadir/bin/javac"
    export converter="$jcdir/bin/converter"
    export scriptgen="$jcdir/bin/scriptgen"

    export classpath="$jcdir3_5/lib/api_classic.jar:$jcdir3_5/lib/api_classic_annotations.jar:$jcdir3_5/lib/tools.jar:$jcdir3_5/lib/jctasks.jar:$jcdir3_5/lib/ant-contrib-1.0b3.jar:."
    export exportpath="$jcdir3_5/api_export_files:build"

    export packages="vulns applets"
fi

echo "*** Compiling source files ***"
# perform a clean up
for package in "$packages"; do
   rm "classes/com/se/$package/*.class"
   rm "build/com/se/$package/javacard/*.exp"
   rm "build/com/se/$package/javacard/*.cap"
   rm "build/com/se/$package/javacard/*.jca"
done

rm "script/install1.scr"
rm "script/install2.scr"
rm "script/test.scr"

echo "$classpath"
"$javac" -classpath "$classpath" -d classes src/*.java

"$converter" -classdir classes -i -d build -out EXP CAP JCA -exportpath "$exportpath" com.se.vulns 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x2 1.0
# "$converter" -classdir classes -i -d build -out EXP CAP JCA -exportpath "$exportpath" -applet 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1:0x1 com.se.applets.SEApplet com.se.applets 0xa0:0x0:0x0:0x0:0x62:0x3:0x1:0xc:0x1 1.0


# x=dirname "$(realpath $0)"
# pushd ../g_gen
# # build.sh
# run.sh "$x/$poc/build/com/se/vulns/javacard/vulns.cap" "$x/$poc/build/com/se/vulns/javacard/vulns.exp" "$x/$poc/build/com/se/vulns/javacard/vulns.new.cap" "%genidx%" "%genarg%"
# popd #"$x/$poc"

# "$scriptgen" build/com/se/vulns/javacard/vulns.new.cap -o script/install1.scr
# "$scriptgen" build/com/se/applets/javacard/applets.cap -o script/install2.scr

# cp script/powerup.scr script/test.scr
# cat script/install1.scr >> script/test.scr
# cat script/install2.scr >> script/test.scr
# cat test.scr >> script/test.scr
# cat script/powerdown.scr >> script/test.scr
