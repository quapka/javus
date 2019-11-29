General:
Gemalto reader very sensitive to proper card insertion (troubles with card F)

transaction-confusion
- install non-malicious
- [remove non-malicious]
- instll malicious
- INS_PREPARE1
- INS_PREPARE2
- INS_READMEM

illega-cast
- install


212 version
Card A:
    transaction-confusion
    - cannot install any version
    illega-cast
    - install
    INSTALL [for load] failed: 0x6F00

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

Card C:
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

