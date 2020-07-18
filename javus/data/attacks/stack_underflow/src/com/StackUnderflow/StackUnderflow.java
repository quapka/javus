/** Copyright 2016 Riscure */
package com.stackunderflow;

import javacard.framework.*;

/**
 * @aid 0xA0:0x00:0x00:0x00:0x00:0x07:0x01
 * @version 1.0
 */
public class StackUnderflow extends Applet {
  protected static final byte CLA_APP = (byte) 0xA0; // regular APDU CLASS byte
  protected static final byte INS_READ = (byte) 0xB0; // INS byte to read data from file
  short[] st = {1, 2, 3, 4};

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new StackUnderflow(bArray, bOffset, bLength);
  }

  protected StackUnderflow(byte[] bArray, short bOffset, byte bLength) {
    register();
  }

  public void process(APDU apdu) {
    short offset, length;
    byte[] buffer = apdu.getBuffer();
    if (selectingApplet()) return;
    if (buffer[ISO7816.OFFSET_CLA] != CLA_APP) ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);

    switch (buffer[ISO7816.OFFSET_INS]) {
      case INS_READ: // read from arbitrary memory position
        offset = Util.getShort(buffer, ISO7816.OFFSET_P1);

        m1((short) 0xD0D0, (short) 0x1F1F);
        for (short i = 0; i < (short) st.length; i++) {
          Util.setShort(buffer, (short) (2 * i), (short) st[i]);
        }
        apdu.setOutgoingAndSend((short) 0, (short) st.length);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }
  // method is used to analyze the stack content
  public short m1(short s1, short s2) {
    short lm11 = (short) 0x1111;
    short lm12 = (short) 0x1212;
    foo();
    return (short) 0x1717;
  }

  public void foo() {
    short s1 = 0;
    short s2 = 0;
    short s3 = 0;
    short s4 = 0;
    /* // modify in JCA
    dup2;
    sstore 1;
    sstore 2;
    sstore 3;
    sstore 4;
    */
    st[0] = s1;
    st[1] = s2;
    st[2] = s3;
    st[3] = s4;
    return;
  }
}
