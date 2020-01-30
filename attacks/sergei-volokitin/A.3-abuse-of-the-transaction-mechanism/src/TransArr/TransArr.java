// package com.transaction_ref;

// import javacard.framework.*;

// public class TransArr extends Applet {
//     private static final byte INS_SUCCESS = 0x01;
//     private static final byte INS_FAILURE = 0x02;

//     byte[] success = {(byte) 0x01, (byte) 0x02, (byte) 0x01, (byte) 0x02};
//     byte[] failure = {(byte) 0x80, (byte) 0x40, (byte) 0x80, (byte) 0x40};
//     short msgLen = 4;

//     public static void install(byte[] array, short off, byte len) {
//         new TransArr().register();
//     }
//     public void process(APDU apdu) {
//         if (selectingApplet()) { return; }

//         byte[] buf = apdu.getBuffer();
//         switch (buf[ISO7816.OFFSET_INS]) {
//             case INS_SUCCESS:
//                 Util.arrayCopyNonAtomic(success, (short) 0, buf, (short) 0, msgLen);
//                 apdu.setOutgoingAndSend((short) 0, (short) 4);
//                 break;
//             case INS_FAILURE:
//                 Util.arrayCopyNonAtomic(failure, (short) 0, buf, (short) 0, msgLen);
//                 apdu.setOutgoingAndSend((short) 0, (short) 4);
//                 break;
//             default:
//                 ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
//         }
//     }

// }
/**
* Copyright 2016 Riscure
*/
package com.transaction_ref;
import javacard.framework.*;

/**
* @aid 0xA0:0x00:0x00:0x00:0x33:0x33:0x01
* @version 1.0
*/

public class TransArr extends Applet
{
    protected final static byte CLA_APP = (byte) 0xA0; // CLASS byte for regular APDUs
    protected final static byte INS_A = (byte) 0xB1; // INS byte to execute a transaction
    short[] trArrS;

    public static void install( byte[] bArray, short bOffset, byte bLength ) {
        new TransArr(bArray, bOffset, bLength);
    }

    protected TransArr(byte[] bArray, short bOffset, byte bLength) {
        register();
    }

    public void process(APDU apdu) {
    byte[] buffer;
    short[] localArrS;
    buffer = apdu.getBuffer();
    if (selectingApplet()) {return;}
    switch(buffer[ISO7816.OFFSET_INS]) {
        case INS_A:
            trArrS = null;
            localArrS = null;

            JCSystem.beginTransaction();
            trArrS = new short[1];
            localArrS = trArrS;
            JCSystem.abortTransaction();

            if (localArrS != null) {
                Util.setShort(buffer, (short)0, (short)addr(trArrS));
            }
            apdu.setOutgoingAndSend( (short)0, (short)2);
            break;
        default:
            ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }

    public static short addr( Object ptr ) {
        //return (short)ptr;
        return 0; // dummy statement
    }
}
