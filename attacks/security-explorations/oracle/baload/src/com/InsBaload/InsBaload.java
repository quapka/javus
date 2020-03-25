package com.baload;

import javacard.framework.*;

public class InsBaload extends Applet {
  private static final byte INS_SUCCESS = (byte) 0x01;
  private static final byte INS_FAILURE = (byte) 0x02;

  private static final byte INS_READ = (byte) 0x04;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  byte[] NOP = {};
  short msgLen = 4;

  byte[] array = new byte[1];

  public static void install(byte[] array, short off, byte len) {
    new InsBaload().register();
  }

  public void process(APDU apdu) {
    short value;
    if (selectingApplet()) {
      return;
    }

    byte[] buf = apdu.getBuffer();
    switch (buf[ISO7816.OFFSET_INS]) {
      case INS_SUCCESS:
        Util.arrayCopyNonAtomic(success, (short) 0, buf, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      case INS_FAILURE:
        Util.arrayCopyNonAtomic(failure, (short) 0, buf, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      case INS_READ:
        check_received_bytes(apdu, buf);
        // read P1 value from the APDU buffer
        value = Util.getShort(buf, ISO7816.OFFSET_P1);
        success[0] = 1;
        // try to save a value outside of the allowed bounderies
        success[0] = success[value];
        // Util.setShort(buf, (short) (0), value);
        Util.arrayCopyNonAtomic(success, (short) 0, buf, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 2);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }

  public void check_received_bytes(APDU apdu, byte[] buffer) {
    byte numBytes = buffer[ISO7816.OFFSET_LC];

    // necessary for 2.1.2 versions!
    byte byteRead = (byte) apdu.setIncomingAndReceive();

    if (numBytes != byteRead) {
      ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
    }
  }
}
