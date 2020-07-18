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
 short dummy;
 short dummy2;

 Object field_a;
 byte field_b;
 short field_s;
 short dummy5;
 short dummy6;
 short dummy7;

 static int imem[];
 static Test t;

 public static final byte IMEM_SIZE = 2;

 public Test() {
  dummy=0x1234;
  dummy2=0x5678;
 }

 public static int[] imem() {
  return imem;
 }

 public static void init() {
  if (t==null) {
   imem=new int[IMEM_SIZE];
   imem[0]=0x11223344;
   imem[1]=0x55667788;

   t=new Test();
  }
 }

 public static Object getfield_a() {
  init();

  return t.field_a;
 }

 public static void putfield_a(Object o) {
  init();

  t.field_a=o;
 }

 public static byte getfield_b() {
  init();

  return t.field_b;
 }

 public static void putfield_b(byte b) {
  init();

  t.field_b=b;
 }

 public static short getfield_s() {
  init();

  return t.field_s;
 }

 public static void putfield_s(short len) {
  init();

  t.field_s=len;
 }

 public static short cast2short(Object o,short s) {
  return s;
 }

 public static Object cast2obj(Object o,short s) {
  return o;
 }
}
