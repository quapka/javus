package illegalcasting;

import javacard.framework.*;

public class IllegalCasting extends Applet {
    private static final byte INS = 0x01;

    byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
    byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
    short msgLen = 4;

    // static byte[] ba = {0x00, 0x01, 0x02};
    // static short[] sa = {(short[]) ptr( addr( ba ) );
    public static void install(byte[] array, short off, byte len) {
        new IllegalCasting().register();
    }
    public void process(APDU apdu) {
        if (selectingApplet()) { return; }

        byte[] buf = apdu.getBuffer();
        short[] addr = null;
        switch (buf[ISO7816.OFFSET_INS]) {
            case INS:
                for (short i = 0; i < 100; i++) {
                    short[] addr = (short[]) ptr;
                    // if((Object) i != null) {
                    //     Util.arrayCopyNonAtomic(success, (short) 0, buf, (short) 0,  msgLen);
                    //     apdu.setOutgoingAndSend((short) 0, msgLen);
                    // }
                }
                break;
            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    public static short addr(Object o) {
        return o;
    }
    public static Object ptr(short addr) {
        return addr;
    }
}
