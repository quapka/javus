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

    private final static byte READ_MEM          = (byte)0x10;
    private final static byte WRITE_MEM         = (byte)0x11;
    
    private static final short BUFLEN           = 64;

    private byte[] bmem;

    protected SEApplet() {       
      register();
    }

    public static void install(byte[] bArray, short bOffset, byte bLength) {
      new SEApplet();
    }

    public byte[] bmem() {
     bmem=Cast.bmem();

     return bmem;
    }

    public byte[] get_req(APDU apdu) {
      byte[] buffer=apdu.getBuffer();

      byte byteRead=(byte)(apdu.setIncomingAndReceive());

      return buffer;
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

    public void read_mem(APDU apdu) {
     byte buf[]=get_req(apdu,(short)4);

     int off=(((int)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(int)8;
     off|=(((int)buf[ISO7816.OFFSET_CDATA+1])&0xff);

     int len=(((int)buf[ISO7816.OFFSET_CDATA+2])&0xff);
     int type=(((int)buf[ISO7816.OFFSET_CDATA+3])&0xff);

     if (len>BUFLEN) len=BUFLEN;

     byte srcmem[]=Cast.bmem();
     byte dstmem[]=new byte[(short)(len)];

     if (type==0) {
      Util.arrayCopy(srcmem,(short)off,dstmem,(short)0,(short)len);
     } else {
      Util.arrayCopyNonAtomic(srcmem,(short)off,dstmem,(short)0,(short)len);
     }

     for(int i=0;i<len;i++) {
      byte v=dstmem[(short)(i)];
      buf[(short)(ISO7816.OFFSET_CDATA+i)]=(byte)(v);
     }

     send_resp(apdu,(short)len);
    }

    public void write_mem(APDU apdu) {
     byte buf[]=get_req(apdu);

     byte numBytes=buf[ISO7816.OFFSET_LC];

     if (numBytes<4) {
        ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
     }

     int off=(((int)buf[ISO7816.OFFSET_CDATA+0])&0xff)<<(int)8;
     off|=(((int)buf[ISO7816.OFFSET_CDATA+1])&0xff);

     int len=(((int)buf[ISO7816.OFFSET_CDATA+2])&0xff);
     int type=(((int)buf[ISO7816.OFFSET_CDATA+3])&0xff);

     if (len>BUFLEN) len=BUFLEN;

     if ((len+4)>numBytes) {
        ISOException.throwIt(ISO7816.SW_WRONG_LENGTH);
     }

     byte srcmem[]=new byte[(short)(len)];

     for(int i=0;i<len;i++) {
      byte v=buf[(short)(ISO7816.OFFSET_CDATA+4+i)];
      srcmem[(short)i]=(byte)(v);
     }

     byte dstmem[]=Cast.bmem();

     if (type==0) {
      Util.arrayCopy(srcmem,(short)0,dstmem,(short)off,(short)len);
     } else {
      Util.arrayCopyNonAtomic(srcmem,(short)0,dstmem,(short)off,(short)len);
     }

     send_resp(apdu,(short)0);
    }

    public void process(APDU apdu) {
      byte[] buffer=apdu.getBuffer();

      if (buffer[ISO7816.OFFSET_CLA]!=SEApplet_CLA) {
       ISOException.throwIt(ISO7816.SW_CLA_NOT_SUPPORTED);
      }

      switch (buffer[ISO7816.OFFSET_INS]) {
        case READ_MEM:
         read_mem(apdu);
         return;
        case WRITE_MEM:
         write_mem(apdu);
         return;
        default:
         ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
      }
    }
}

