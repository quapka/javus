#!/bin/bash
function gp() {
    java -jar "$GO_PATH" $@
}

#TODO maybe use the --dump flag to dump the APDU communication and parse that one later
echo "Getting the information from '--info' flag"
gp --info
echo "Getting the list of applets from '--list' flag"
gp --list
echo "Getting the list of privileges from '--list-privs' flag"
gp --list-privs

echo "Getting the JavaCard version from JCVersion applet"
make && make install
gp --debug --apdu 00a40400050011223344 --apdu 0b040000
