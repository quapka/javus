package com.cryptopkg;

import javacard.framework.*;
import javacardx.crypto.*;

public class CryptoPkg extends Applet {
    // define the instructions
    private static final byte INS_PREPARE = 0x01;
    private static final byte INS_ATTACK = 0x02;
    // define values for simulating an attack
    byte[] prepare = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
    byte[] secret = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
    short msgLen = 4;

    public static void install(byte[] array, short off, byte len) {
        new CryptoPkg().register();
    }
    public void process(APDU apdu) {
        if (selectingApplet()) { return; }

        // Make sure javacardx.crypto package is included
        Cipher aesCipher = Cipher.getInstance(Cipher.ALG_AES_BLOCK_128_ECB_NOPAD, false);

        byte[] buf = apdu.getBuffer();
        switch (buf[ISO7816.OFFSET_INS]) {
            case INS_PREPARE:
                // Here we could do some preparation, maybe mangle some addresses etc.
                // In this example we simply return an arbitrary array and won't do
                // any setup.
                Util.arrayCopyNonAtomic(prepare, (short) 0, buf, (short) 0, msgLen);
                apdu.setOutgoingAndSend((short) 0, (short) 4);
                break;
            case INS_ATTACK:
                // Thanks to the previous instruction, that did some setup we can
                // now call this instruction and e.g. read out some secret memory.
                // Again, in this example we simply return a class array.
                Util.arrayCopyNonAtomic(secret, (short) 0, buf, (short) 0, msgLen);
                apdu.setOutgoingAndSend((short) 0, (short) 4);
                break;
            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

}
