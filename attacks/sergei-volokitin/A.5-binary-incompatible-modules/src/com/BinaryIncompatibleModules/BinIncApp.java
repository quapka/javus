/*
 * Copyright 2016 Riscure All rights reserved.
 */

package binaryincompatible.app;

import binaryincompatible.server.Server;
import javacard.framework.*;

/** @aid 0xA0:0x00:0x00:0x00:0x01:0x01:0x01 */
public class BinIncApp extends Applet {
  protected static final byte CLA = (byte) 0xA0;
  protected static final byte INS_READ = (byte) 0xB0;
  short[] sBuffer = {};

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new BinIncApp(bArray, bOffset, bLength);
  }

  public BinIncApp(byte[] bArray, short bOffset, byte bLength) {
    register();
  }

  public void process(APDU apdu) {
    byte[] buffer = apdu.getBuffer();

    short length;

    if (selectingApplet()) return;

    switch (buffer[ISO7816.OFFSET_INS]) {
      case INS_READ:
        sBuffer = Server.convertRef(ba2);
        length = (short) sBuffer.length;
        for (short i = 0; i < length; i++) {
          Util.setShort(buffer, (short) (2 * i), sBuffer[i]);
        }
        apdu.setOutgoingAndSend((short) 0, length);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }
}
