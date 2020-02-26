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
  // static short value = 255;
  short value = 255;

  // static byte[] name = new byte[255];
  byte[] name = new byte[255];

  protected CardName(byte[] buffer, short offset, byte length) {
    register();
  }

  public static void install(byte[] buffer, short offset, byte length) {
    // byte AIDLen = buffer[offset];
    // byte controlLen = buffer[(short)(offset + AIDLen + 1)];
    // byte dataLen = buffer[(short)(offset + AIDLen + 1 + controlLen + 1)];
    // if (dataLen != 0) {
    //     value = dataLen > (short)255 ? (short)255 : dataLen;
    //     Util.arrayCopy(buffer, (short)(offset + AIDLen + 1 + controlLen + 1 + 1), name, (short)0,
    // value);
    // }
    // new CardName().register();
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
        // Util.arrayCopyNonAtomic(buf, (short) buf[ISO7816.OFFSET_CDATA], name, (short) 0,
        // buf[ISO7816.OFFSET_LC]);
        // short dest_plus_len = 0;
        // dest_plus_len =
        // Util.arrayCopy(buf, (short) ISO7816.OFFSET_CDATA, name, (short) 0, (short)
        // buf[ISO7816.OFFSET_LC]);
        value = Util.makeShort(buf[ISO7816.OFFSET_CDATA + 1], buf[ISO7816.OFFSET_CDATA]);
        // value = (short) buf[ISO7816.OFFSET_LC];
        Util.setShort(name, (short) 0, value);
        Util.arrayCopy(name, (short) 0, buf, (short) 0, (short) 2);
        apdu.setOutgoingAndSend((short) 0, (short) 2);
        break;
      case INS_GET_NAME:
        Util.arrayCopy(name, (short) 0, buf, (short) 0, value);
        apdu.setOutgoingAndSend((short) 0, value);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }
}
