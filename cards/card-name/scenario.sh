#!/bin/bash

function gp() {
    java -jar "$GO_PATH" "$@"
}

echo "Start scenario."
echo "Make sure the applet is not installed:"
make uninstall
echo "Make the project from scratch:"
make

echo
echo "Install the Applet with the name set to 'C0FFEE'."
gp --verbose --debug --install com.card_name.cap --params C0FFEE

echo
echo "Read out the name from the card:"
gp --verbose --debug --apdu 00A40400080011223344AABBCC --apdu 00080000

echo
echo "Change the name of the card to 'DEADBEEF'."
gp --verbose --debug --apdu 00A40400080011223344AABBCC --apdu 0004000004DEADBEEF

echo
echo "Read out the name from the card again:"
gp --verbose --debug --apdu 00A40400080011223344AABBCC --apdu 00080000

echo "End scenario."
