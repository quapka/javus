#!/usr/bin/env python

import smartcard
import logging
from jcvmutils.classes import CommunicateWithCard

# import jcvmutils.jcvmutils.class

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

# TODO don't forget about diversifiers


class SendAPDUs(CommunicateWithCard):
    def __init__(self):
        self.input_file = None
        super().__init__()

    def add_options(self):
        super().add_options()
        self.parser.add_argument(
            "-i", "--input-file", help="input scr file", required=True,
        )

    def parse_options(self):
        super().parse_options()
        if self.args.input_file is not None:
            self.input_file = self.args.input_file

    # TODO add validate_scr_file
    def create_apdus(self):
        self.payloads = []
        with open(self.input_file, "r") as f:
            for line in f.readlines():
                line = line.strip()
                if line.startswith("//"):
                    print(line.lstrip("/"))

                if not line.startswith("0x"):
                    continue

                values = line.strip(";").split()
                # import pudb; pudb.set_trace()
                payload = [int(x, 16) for x in values]
                print("".join(["{:02x}".format(x) for x in payload]))
                self.payloads.append(payload)

    def send_apdus(self):
        self.select()

        for payload in self.payloads:
            response = self.transmit(payload)
            self.print_response(response)

    def transmit(self, payload):
        # try:
        #     data, sw = self.card.transmit(payload, protocol=self.protocol)
        # except smartcard.Exceptions.CardConnectionException:
        #     log.error("Cannot tranmsit bytes to the card? Try running again.")

        return self.card.transmit(payload, protocol=self.protocol)

    def print_response(self, response):
        data, sw1, sw2 = response
        print(data, sw1, sw2)
        line = "{:02X}{:02X}".format(sw1, sw2)
        line += ": " + " ".join(["{:02X}".format(x) for x in data])
        print(line)

    def select(self):
        SELECT_BYTES = [0x00, 0xA4, 0x04, 0x00]
        #
        AID = [0x00, 0x11, 0x22, 0x33, 0x44, 0xAA, 0xBB]

        payload = SELECT_BYTES + [len(AID)] + AID
        self.transmit(payload)

    def run(self):
        self.create_apdus()
        # self.send_apdus()


if __name__ == "__main__":
    app = SendAPDUs()
    app.run()
