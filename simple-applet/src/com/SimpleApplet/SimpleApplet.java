package com.simple;

import javacard.framework.*;

public class SimpleApplet extends javacard.framework.Applet {
  byte HELLO[] = {
    (byte) 0x48,
    (byte) 0x65,
    (byte) 0x6c,
    (byte) 0x6c,
    (byte) 0x6f,
    (byte) 0x20,
    (byte) 0x77,
    (byte) 0x6f,
    (byte) 0x72,
    (byte) 0x6c,
    (byte) 0x64,
    (byte) 0x21
  };

  protected SimpleApplet(byte[] buffer, short offset, byte length) {
    register();
  }

  public static void install(byte[] bArray, short bOffset, byte bLength) throws ISOException {
    new SimpleApplet(bArray, bOffset, bLength);
  }

  public void process(APDU apdu) throws ISOException {
    // get the APDU buffer
    byte[] apduBuffer = apdu.getBuffer();
    // ignore the applet select command dispached to the process
    if (selectingApplet()) {
      return;
    }
    // For Hello world, just copy message
    Util.arrayCopyNonAtomic(HELLO, (short) 0, apduBuffer, (short) 0, (short) HELLO.length);
    apdu.setOutgoingAndSend((short) 0, (short) HELLO.length);
  }
}
