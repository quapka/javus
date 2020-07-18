#!/bin/bash
if [ -z "$1" ]; then
    echo "Error: Set jcversion"
    exit 1
fi
jcversion="$1"

# vulns_dir="/home/qup/projects/fi/thesis/attacks/security-explorations/se-2019-01-codes/codes/baload_bastore/build/$jcversion/com/se/vulns/javacard/"
vulns_dir="../baload_bastore/build/$jcversion/com/se/vulns/javacard/"

pushd ../_gen
java Gen\
    "$vulns_dir/vulns.cap"\
    "$vulns_dir/vulns.exp"\
    "$vulns_dir/vulns.new.cap"\
    1 0
gen_status_code="$?"

# echo "$gen_status_code"
# exit "$gen_status_code"
