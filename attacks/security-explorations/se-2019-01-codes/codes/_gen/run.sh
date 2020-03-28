#!/bin/bash
../config.sh

export java="$javadir/bin/java"

"$java" Gen "$1" "$2" "$3" "$4" "$5"
