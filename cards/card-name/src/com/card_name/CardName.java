package com.card_name;

import javacard.framework.*;

public class CardName extends Applet {
  private static final byte INS_SUCCESS = 0x01;
  private static final byte INS_FAILURE = 0x02;
  private static final byte INS_SET_NAME = 0x04;
  private static final byte INS_GET_NAME = 0x08;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  short msgLen = 4;

  short nameLen = 255;
  byte[] name = new byte[255];

  protected CardName(byte[] buffer, short offset, byte length) {
    register();
  }

  public static void install(byte[] buffer, short offset, byte length) {
    new CardName(buffer, offset, length);
  }

  public void process(APDU apdu) {
    if (selectingApplet()) {
      return;
    }

    byte[] buf = apdu.getBuffer();

    switch (buf[ISO7816.OFFSET_INS]) {
      case INS_SUCCESS:
        Util.arrayCopy(success, (short) 0, buf, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      case INS_FAILURE:
        Util.arrayCopy(failure, (short) 0, buf, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      case INS_SET_NAME:
        byte numBytes = buf[ISO7816.OFFSET_LC];

        // necessary for 2.1.2 versions!
        byte byteRead = (byte) apdu.setIncomingAndReceive();

        if (numBytes != byteRead) {
          ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
        }

        Util.arrayCopy(buf, (short) ISO7816.OFFSET_CDATA, name, (short) 0, buf[ISO7816.OFFSET_LC]);
        nameLen = (short) buf[ISO7816.OFFSET_LC];

        apdu.setOutgoingAndSend((short) 0, (short) 2);
        break;
      case INS_GET_NAME:
        Util.arrayCopy(name, (short) 0, buf, (short) 0, nameLen);
        apdu.setOutgoingAndSend((short) 0, nameLen);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }
}
