General:
Gemalto reader very sensitive to proper card insertion (troubles with card F)

transaction-confusion
- install non-malicious
- [remove non-malicious]
- instll malicious
- INS_PREPARE1
- INS_PREPARE2
- INS_READMEM

illegal-cast
- install
- INS_READ

metadatamanipulation
- INS_PATCH


212 version
Old Card A:
    transaction-confusion
    - cannot install any version

    illega-cast
    - install
    INSTALL [for load] failed: 0x6F00

    metadata
    - install
    INSTALL [for load] failed: 0x6F00

New card A:
    transaction-confusion
    - install fine
    - INS_PREPARE1 -> 6F00
    - INS_PREPARE2 -> 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000
    - uninstall

    illegal-cast2
    - install non-malicious fine
        - uninstall
    - install malicious 
    - INS_READ A0B0000000 -> 9000
    - INS_READ A0B0010000 -> 6F00
    - INS_READ A0B0BB0000 -> 6F00
    - INS_READ A0B0CC0000 -> 6F00
    - INS_READ A0B0FF0000 -> 6F00

    metadatamanipulation
    - install non-malicious fine
    - INS_PATCH a0b4000000 -> 6F00
    - install malicious fine
    - INS_PATCH a0b4000000 -> 6F00
    - --delete first applet then the package worked

Card B:
    transaction-confusion
    - INS_PREPARE1 returns 6A80 = SW_WRONG_DATA <-- raised by the code itself
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illega-cast
    - install non-malicious fine
        - uninstall fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0010000 -> 6F00 SW_UNKNOWN
    - INS_READ a0b0BB0000 -> SCARD_E_NOT_TRANSACTED
    - INS_READ a0b0CC0000 -> SCARD_E_NOT_TRANSACTED
    - INS_READ a0b0FF0000 -> SCARD_E_NOT_TRANSACTED

Old Card C:
    transaction-confusion, tried twice, card goes to LOCKED each time
    - can install 212
    - can INS_PREPARE1
    - INS_PREPARE2 gets applet LOCKED

    illegal-cast
    - can install non-malicious
    - can install malicious
    - INS_READ a0b0000000 -> 9000; a0b0010000, a0b0020000 -> 6F00
    - a0b0ff0000 -> LOCKED
    - end up in a LOCK, cannot delete/uninstall

    metadata
    - install non-malicious fine
    - install malicious fine
    - INS_PATCH -> SCARD_E_NOT_TRANSACTED
    - uninstall

New Card c:
    transaction-confusion
    1st run
    - install (malicious) fine
    - INS_PREPARE1 apdu 80010000 00 -> 0080080 9000
    - INS_PREPARE2 apdu 80020000 00 -> 6F00
        >> APPLET LOCKED
    - INS_READMEM returns 6A82 for SELECT
    - 6D00 for SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000
    2nd run
    - INS_PREPARE1 apdu 80010000 00 -> 0080080 9000


    illegal-cast
    -

    metadatamanipulation
    -


Card D:
    transaction-confusion
    - INS_PREPARE1 returns 6A80 = SW_WRONG_DATA <-- raised by the code itself
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious fine
        - uninstall fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0010000 -> SCARD_E_NOT_TRANSACTED
    - INS_READ a0b0BB0000 -> SCARD_E_NOT_TRANSACTED
    - INS_READ a0b0CC0000 -> SCARD_E_NOT_TRANSACTED
    - INS_READ a0b0FF0000 -> SCARD_E_NOT_TRANSACTED

Card E:
    transaction-confusion
    - can install 212
    - can INS_PREPARE2
    - INS_PREPARE2 does not LOCK the card
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious fine
    - uninstall non-malicious fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0010000 -> SCARD_E_NOT_TRANSACTED

    metadatamanipulation
    - install non-malicious fine
        - uninstall
    - install malicious
    - INS_PATCH -> SCARD_E_NOT_TRANSACTED


Card F:
    transaction-confusion
    - INS_PREPARE1 seems to kill the application
    SCARD_E_NOT_TRANSACTED =  An attempt was made to end a non-existent transaction. 
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0BB0000 -> 9000
    - INS_READ a0b0CC0000 -> 9000
        non of the above returns any data
    - INS_READ a0b0010000 -> 6F00 SW_UNKNOWN

    metadata
    - install non-malicious fine
    - install malicious fine
    - INS_PATCH A0B40000 -> 7FFF

Card G:
    transaction-confusion
    - INS_PREPARE1
    SCARD_E_NOT_TRANSACTED =  An attempt was made to end a non-existent transaction. 
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious fine
        - uninstall failed 6a86 SW_INCORRECT_P1P2
        - --delete AID worked - not really, later install showed it is still there
    - install malicious force install
    - is not SELECTABLE

    metadata
    - can't install
        - deletion fails for package
        gp --delete A0000000AA
        Deletion failed: 0x6A86 (Incorrect P1/P2)
    - install non-malicious fine
    - install malicious fine
    - INS_PATCH A0B40000 -> 7FFF


Card H:
    transaction-confusion
    - INS_PREPARE1
    SCARD_E_NOT_TRANSACTED =  An attempt was made to end a non-existent transaction.
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious -> 6985 SW_CONDITIONS_NOT_SATISFIED (applet was already there!)
        - first --delete applet, then --delete package
    - installs non-malicious fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0010000 -> 6F00 SW_UNKNOWN
    - INS_READ a0b0BB0000 -> 6F00 SW_UNKNOWN
    - INS_READ a0b0CC0000 -> 9000
    - INS_READ a0b0FF0000 -> 9000

    metadata
    - can't install deletion fails Deletion failed: 0x6A86 (Incorrect P1/P2)
    - install non-malicious fine
    - install malicious fine
    - INS_PATCH A0B40000 -> 7FFF



Card I:
    transaction-confusion
    - INS_PREPARE1
    SCARD_E_NOT_TRANSACTED =  An attempt was made to end a non-existent transaction.
    - INS_PREPARE2 6F00
    - INS_READMEM returns 6F00  SW_UNKNOWN for addresses: 0000 0020 3017 3201 4000 5000

    illegal-cast
    - install non-malicious fine
         - uninstall fine
    - install malicious fine
    - INS_READ a0b0000000 -> 9000
    - INS_READ a0b0010000 -> 6F00 SW_UNKNOWN
    - INS_READ a0b0BB0000 -> 6F00 SW_UNKNOWN
    - INS_READ a0b0FF0000 -> later got 6a82  SW_FILE_NOT_FOUND, got locked

    metadata
    - can't install deletion fails Deletion failed: 0x6A86 (Incorrect P1/P2)
    - install non-malicious fine
    - install malicious fine
    - INS_PATCH A0B40000 -> 6F00


