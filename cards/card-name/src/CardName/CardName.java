package com.card_name;

import javacard.framework.*;

public class CardName extends Applet {
    private static final byte INS_SUCCESS = 0x01;
    private static final byte INS_FAILURE = 0x02;
    private static final byte INS_SET_NAME = 0x04;
    private static final byte INS_GET_NAME = 0x08;

    byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
    byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
    short msgLen = 4;
    static short nameLen = 255;

    static byte[] name = new byte[255];

    public static void install(byte[] buffer, short offset, byte length) {
        byte AIDLen = buffer[offset];
        byte controlLen = buffer[(short)(offset + AIDLen + 1)];
        byte dataLen = buffer[(short)(offset + AIDLen + 1 + controlLen + 1)];
        if (dataLen != 0) {
            nameLen = dataLen > (short)255 ? (short)255 : dataLen;
            Util.arrayCopy(buffer, (short)(offset + AIDLen + 1 + controlLen + 1 + 1), name, (short)0, nameLen);
        }
        new CardName().register();
    }

    public void process(APDU apdu) {
        if (selectingApplet()) { return; }

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
            case INS_SET_NAME:
                // Util.arrayCopyNonAtomic(buf, (short) buf[ISO7816.OFFSET_CDATA], name, (short) 0, buf[ISO7816.OFFSET_LC]);
                Util.arrayCopyNonAtomic(buf, (short) ISO7816.OFFSET_CDATA, name, (short) 0, (short)buf[ISO7816.OFFSET_LC]);
                nameLen = (short) buf[ISO7816.OFFSET_LC];
                apdu.setOutgoingAndSend((short) 0, nameLen);
                break;
            case INS_GET_NAME:
                Util.arrayCopyNonAtomic(name, (short) 0, buf, (short) 0, nameLen);
                apdu.setOutgoingAndSend((short) 0, nameLen);
                break;
            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

}
