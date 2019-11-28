package com.shareableinterfacemaster;

import javacard.framework.*;

public class ShareableInterfaceMaster extends Applet implements MyInterface {
  private static final byte INS_SUCCESS = 0x01;
  private static final byte INS_FAILURE = 0x02;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  byte[] master = {(byte) 0x6D, (byte) 0x61, (byte) 0x73, (byte) 0x74, (byte) 0x65, (byte) 0x72};
  short msgLen = 4;

  public static void install(byte[] array, short off, byte len) {
    new ShareableInterfaceMaster().register();
  }

  public void process(APDU apdu) {
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
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }

  public byte[] giveArray() {
    // byte[] array = {}; // {(byte) 0x6D, (byte) 0x61, (byte) 0x73, (byte) 0x74, (byte) 0x65,
    // (byte)
    // 0x72};
    // return array;
    return master;
  }

  public void accessArray(short[] myArray) {
    byte[] array = {};
  }

  public void test() {
    byte[] nop = {};
  }
}
