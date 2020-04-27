import argparse
import logging
import sys

import smartcard
from jsec.utils import CommandLineApp
from smartcard.CardConnection import CardConnection
from smartcard.System import readers
from smartcard.util import toHexString

log = logging.getLogger(__file__)
handler = logging.StreamHandler()
# TODO update for formatter to show the name of the package as well
formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)

LOG_LEVELS = [
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]
SELECT_BYTES = [0x00, 0xA4, 0x04, 0x00]


class CommunicateWithCard(CommandLineApp):
    NO_CARDS_DETECTED_ERROR = -1
    TOO_MANY_CARDS_DETECTED_ERROR = -2

    def __init__(self):
        self.card = None
        self.protocol = None
        self.readers = None
        super().__init__()
        log.setLevel(self.verbosity)

        self.load_readers()
        self.detect_card()
        self.detect_protocol()

    def load_readers(self):
        log.debug("Loading smartcard readers")
        self.readers = readers()
        names = " ".join(["'" + str(r) + "'" for r in self.readers])
        log.debug("Loaded: %s ", names)

    # def add_options(self):
    #     super().add_options()
    #     self.parser.add_argument(
    #         '-short-option', '--long-option',
    #         help='Help message',
    #         type=self.validate_option,
    #     )

    def parse_options(self):
        super().parse_options()
        # if self.args.long_option is not None:
        #     self.long_option = self.args.long_option

    # def validate_name(self, value):
    #     """Expects value to be 'ascii' string
    #     """
    #     if len(value) > 256:
    #         raise argparse.ArgumentTypeError("The name '{}' is too long".format(value))
    #     try:
    #         return list(bytes(value, "ascii"))
    #     except UnicodeDecodeError:
    #         raise argparse.ArgumentTypeError(
    #             "The name '{}' contains non-ascii characters".format(value)
    #         )

    def detect_card(self):
        cards = []
        for reader in self.readers:
            con = reader.createConnection()
            try:
                con.connect()
            except smartcard.Exceptions.NoCardException:
                continue

            cards.append(con)
            atr = bytes(con.getATR()).hex()
            log.debug("A card [ATR: %s] has been connected", atr)

        if len(cards) < 1:
            log.error("No cards have been detected! Insert only one card.")
            sys.exit(self.NO_CARDS_DETECTED_ERROR)

        if len(cards) > 1:
            log.error("Too many cards have been detected! Insert only one card.")
            sys.exit(self.TOO_MANY_CARDS_DETECTED_ERROR)

        # log.debug("Card '{}' has been selected.".format)
        self.card = cards[0]

    def detect_protocol(self):
        # TODO maybe simplify and use self.card.getProtocol()
        log.debug("Get supported protocols.")
        self.protocol = self.card.getProtocol()

        if self.protocol == CardConnection.T0_protocol:
            log.debug("T0 protocol is used.")
            return

        if self.protocol == CardConnection.T1_protocol:
            log.debug("T1 protocol is used.")
            return

        if self.protocol == CardConnection.T15_protocol:
            log.debug("T15 protocol is used.")
            return

        raise RuntimeError("No protocol supported!")

    def send_apdu(self, apdu):
        pass

    def run(self):
        raise NotImplementedError


if __name__ == "__main__":
    card_manager = CommunicateWithCard()
    card_manager.run()
