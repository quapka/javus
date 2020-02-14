package com.baload;

import javacard.framework.*;

public class InsBaload extends Applet {
    private static final byte INS_SUCCESS = 0x01;
    private static final byte INS_FAILURE = 0x02;

    byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
    byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
    short msgLen = 4;

    public static void install(byte[] array, short off, byte len) {
        new InsBaload().register();
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
            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

}
