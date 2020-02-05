/** Copyright 2016 Riscure */
package class_type_conf;

import class_type_conf.c1.C1;
import class_type_conf.c2.C2;
import class_type_conf.lib.LibC;
import javacard.framework.*;
import javacard.security.*;

/**
 * @aid 0xA0:0x00:0x00:0x00:0x00:0x01:0x01
 * @version 1.0
 */
public class ClassTypeConf extends Applet {
  protected static final byte CLA_APP = (byte) 0xA0; // CLASS byte for regular APDUs
  protected static final byte INS_SET_EL = (byte) 0xB0; // INS byte perform type confusion

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new ClassTypeConf(bArray, bOffset, bLength);
  }

  protected ClassTypeConf(byte[] bArray, short bOffset, byte bLength) {
    register();
  }

  public void process(APDU apdu) {
    short offset, length, change;
    byte[] ba;
    C1 c1i;
    C2 c2i;
    byte[] buffer = apdu.getBuffer();
    if (selectingApplet()) return;
    if (buffer[ISO7816.OFFSET_CLA] != CLA_APP) ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
    switch (buffer[ISO7816.OFFSET_INS]) {
      case INS_SET_EL:
        offset = Util.getShort(buffer, ISO7816.OFFSET_P1);
        c2i = new C2();
        c1i = LibC.convRef(c2i);
        break;
      default:
        ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
    }
  }
}
