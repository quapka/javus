/*## (c) SECURITY EXPLORATIONS    2019 poland                                #*/
/*##     http://www.security-explorations.com                                #*/

/* RESEARCH MATERIAL:	SE-2019-01                                            */
/* Security vulnerabilities in Java Card                                      */

/* THIS SOFTWARE IS PROTECTED BY DOMESTIC AND INTERNATIONAL COPYRIGHT LAWS    */
/* UNAUTHORISED COPYING OF THIS SOFTWARE IN EITHER SOURCE OR BINARY FORM IS   */
/* EXPRESSLY FORBIDDEN. ANY USE, INCLUDING THE REPRODUCTION, MODIFICATION,    */
/* DISTRIBUTION, TRANSMISSION, RE-PUBLICATION, STORAGE OR DISPLAY OF ANY      */
/* PART OF THE SOFTWARE, FOR COMMERCIAL OR ANY OTHER PURPOSES REQUIRES A      */
/* VALID LICENSE FROM THE COPYRIGHT HOLDER.                                   */

/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS    */
/* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,*/
/* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL    */
/* SECURITY EXPLORATIONS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, */
/* WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF  */
/* OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE     */
/* SOFTWARE.                                                                  */

package com.se.applets;

import com.se.vulns.*;
import javacard.framework.*;

public class SEApplet extends Applet {
    private static final byte SEApplet_CLA = (byte) 0x80;

    private static final byte PING = (byte) 0x10;
    private static final byte STATUS = (byte) 0x11;
    private static final byte SETUP = (byte) 0x12;
    private static final byte READ_MEM = (byte) 0x13;
    private static final byte WRITE_MEM = (byte) 0x14;
    private static final byte CLEANUP = (byte) 0x15;

    private static final short BUFLEN = 64;

    private static byte expidx = 1;

    private byte[] bmem;
    private int[] imem;

    protected SEApplet() {
        register();
    }

    public static void install(byte[] bArray, short bOffset, byte bLength) {
        new SEApplet();
    }

    public byte[] bmem() {
        if (bmem == null) {
            switch (expidx) {
                case 1:
                    bmem = Cast.bmem();
                    break;
            }
        }

        return bmem;
    }

    public int[] imem() {
        if (imem == null) {
            switch (expidx) {
                case 1:
                    imem = Cast.imem();
                    break;
            }
        }

        return imem;
    }

    public void cleanup() {
        if (imem != null) {
            switch (expidx) {
                case 1:
                    Cast.cleanup();
                    break;
            }
        }
    }

    public byte[] get_req(APDU apdu, short size) {
        byte[] buffer = apdu.getBuffer();

        byte numBytes = buffer[ISO7816.OFFSET_LC];
        byte byteRead = (byte) (apdu.setIncomingAndReceive());

        if ((numBytes != size) || (byteRead != size)) {
            ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
        }

        return buffer;
    }

    public void send_resp(APDU apdu, short size) {
        short availBytes = apdu.setOutgoing();

        if (availBytes < size) {
            ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
        }

        apdu.setOutgoingLength((byte) size);
        apdu.sendBytes((short) 5, (short) size);
    }

    public void ping(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 2);

        buf[ISO7816.OFFSET_CDATA + 0] = (byte) 0x12;
        buf[ISO7816.OFFSET_CDATA + 1] = (byte) 0x34;

        send_resp(apdu, (short) 2);
    }

    public void status(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 2);

        byte mem[] = bmem();

        int len = 64;

        for (short i = 0; i < len; i++) {
            buf[(short) (ISO7816.OFFSET_CDATA + i)] = (byte) mem[i];
        }

        send_resp(apdu, (short) len);
    }

    public void setup(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 2);

        int mem[] = imem();

        buf[(short) (ISO7816.OFFSET_CDATA + 0)] = (byte) ((mem.length >> 8) & 0xff);
        buf[(short) (ISO7816.OFFSET_CDATA + 1)] = (byte) ((mem.length) & 0xff);

        send_resp(apdu, (short) 2);
    }

    public void read_mem(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 3);

        int mem[] = imem();

        int off = (((int) buf[ISO7816.OFFSET_CDATA + 0]) & 0xff) << (int) 8;
        off |= (((int) buf[ISO7816.OFFSET_CDATA + 1]) & 0xff);

        int len = (((int) buf[ISO7816.OFFSET_CDATA + 2]) & 0xff);
        len &= 0xfc;

        if (len > BUFLEN) len = BUFLEN;

        for (int i = 0; i < len >> 2; i++) {
            int v = mem[(short) (off + i)];
            buf[(short) (ISO7816.OFFSET_CDATA + i * 4 + 0)] = (byte) ((v >> 24) & 0xff);
            buf[(short) (ISO7816.OFFSET_CDATA + i * 4 + 1)] = (byte) ((v >> 16) & 0xff);
            buf[(short) (ISO7816.OFFSET_CDATA + i * 4 + 2)] = (byte) ((v >> 8) & 0xff);
            buf[(short) (ISO7816.OFFSET_CDATA + i * 4 + 3)] = (byte) ((v) & 0xff);
        }

        send_resp(apdu, (short) len);
    }

    public void write_mem(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 6);

        int mem[] = imem();

        int off = (((int) buf[ISO7816.OFFSET_CDATA + 0]) & 0xff) << (int) 8;
        off |= (((int) buf[ISO7816.OFFSET_CDATA + 1]) & 0xff);

        int val = (((int) buf[ISO7816.OFFSET_CDATA + 2]) & 0xff) << (int) 24;
        val |= (((int) buf[ISO7816.OFFSET_CDATA + 3]) & 0xff) << (int) 16;
        val |= (((int) buf[ISO7816.OFFSET_CDATA + 4]) & 0xff) << (int) 8;
        val |= (((int) buf[ISO7816.OFFSET_CDATA + 5]) & 0xff);

        mem[(short) (off)] = val;

        buf[(short) (ISO7816.OFFSET_CDATA + 0)] = (byte) ((val >> 24) & 0xff);
        buf[(short) (ISO7816.OFFSET_CDATA + 1)] = (byte) ((val >> 16) & 0xff);
        buf[(short) (ISO7816.OFFSET_CDATA + 2)] = (byte) ((val >> 8) & 0xff);
        buf[(short) (ISO7816.OFFSET_CDATA + 3)] = (byte) ((val) & 0xff);

        send_resp(apdu, (short) 4);
    }

    public void cleanup(APDU apdu) {
        byte buf[] = get_req(apdu, (short) 2);

        int mem[] = imem();

        cleanup();

        buf[(short) (ISO7816.OFFSET_CDATA + 0)] = (byte) ((mem.length >> 8) & 0xff);
        buf[(short) (ISO7816.OFFSET_CDATA + 1)] = (byte) ((mem.length) & 0xff);

        send_resp(apdu, (short) 2);
    }

    public void process(APDU apdu) {
        byte[] buffer = apdu.getBuffer();

        if (buffer[ISO7816.OFFSET_CLA] != SEApplet_CLA) {
            ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
        }

        switch (buffer[ISO7816.OFFSET_INS]) {
            case PING:
                ping(apdu);
                return;
            case STATUS:
                status(apdu);
                return;
            case SETUP:
                setup(apdu);
                return;
            case READ_MEM:
                read_mem(apdu);
                return;
            case WRITE_MEM:
                write_mem(apdu);
                return;
            case CLEANUP:
                cleanup(apdu);
                return;
            default:
                ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
        }
    }
}
