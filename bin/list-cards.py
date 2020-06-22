#!/usr/bin/env python

import smartcard
import subprocess

# smartcard.pcsc.PCSCExceptions.EstablishContextException


def main():
    try:
        readers = smartcard.System.readers()
    except smartcard.pcsc.PCSCExceptions.EstablishContextException:
        restart_pcscd_daemon()
        readers = smartcard.System.readers()

    for reader in readers:
        print("Reader : %s" % reader)
        con = reader.createConnection()
        con.connect()
        print("    got ATR: ", con.getATR())


def restart_pcscd_daemon():
    restart_cmd = ["service", "pcscd", "restart"]
    try:
        subprocess.check_output(restart_cmd)
        print("restart pcscd: success")
    except subprocess.CalledProcessError:
        print("restart pcscd: failure")


# def list_cards():
#     for reader in smartcard.System.readers():
#         print("Reader : %s" % reader)
#         try:
#             con = reader.createConnection()
#             con.connect()
#             print("    got ATR: ", con.getATR())
#         except smartcard.pcsc.PCSCExceptions.EstablishContextException:
#             if tries:
#                 restart_pcscd_daemon()
#                 tries -= 1


if __name__ == "__main__":
    main()
