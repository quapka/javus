package com.shareableinterfaceslave;

import javacard.framework.*;

public class ShareableInterfaceSlave extends Applet implements MyInterface {
  private static final byte INS_SUCCESS = 0x01;
  private static final byte INS_FAILURE = 0x02;
  private static final byte INS_CALL_MASTER = 0x04;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  short msgLen = 4;

  public static void install(byte[] array, short off, byte len) {
    new ShareableInterfaceSlave().register();
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
      case INS_CALL_MASTER:
        byte[] array2 = {};
        array2 = callMaster();
        byte[] array = {
          (byte) 0x80, (byte) 0x80, (byte) 0x80, (byte) 0x80, (byte) 0x80, (byte) 0x80
        };
        Util.arrayCopyNonAtomic(array, (short) 0, buf, (short) 0, (short) 6);
        apdu.setOutgoingAndSend((short) 0, (short) 6);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }

  public byte[] giveArray() {
    byte[] array = {};
    return array;
  }

  public void accessArray(byte[] myArray) {}

  public byte[] callMaster() {
    byte[] masterAppletAID = {
      // "000000000104"
      (byte) 0x00, (byte) 0x00, (byte) 0x00, (byte) 0x00, (byte) 0x01, (byte) 0x04
    };
    AID aid = JCSystem.lookupAID(masterAppletAID, (short) 0, (byte) masterAppletAID.length);
    MyInterface MasterAppInstance =
        (MyInterface) JCSystem.getAppletShareableInterfaceObject(aid, (byte) 0);
    MasterAppInstance.test();
    return masterAppletAID;
  }
}
