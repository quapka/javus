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

import java.lang.*;
import java.lang.reflect.*;
import java.util.*;
import java.io.*;
import java.util.jar.*;
import java.util.zip.*;

public class CAPFile {
 static ArrayList components;
 static Hashtable lookup=new Hashtable();

 public static int minor_version;

 public static final String CAP_EXTENSION = ".cap";

 Manifest mf;

 public static int load_order[]={
  Component.COMPONENT_Header,
  Component.COMPONENT_Descriptor,
  Component.COMPONENT_Directory,
  Component.COMPONENT_Applet,
  Component.COMPONENT_Import,
  Component.COMPONENT_ConstantPool,
  Component.COMPONENT_Class,
  Component.COMPONENT_Method,
  Component.COMPONENT_StaticField,
  Component.COMPONENT_ReferenceLocation,
  Component.COMPONENT_Export,
  Component.COMPONENT_Debug
 };

 public Component load_component(String name,InputStream is) throws Throwable {
  Component comp=null;

  DataInputStream dis=new DataInputStream(is);

  byte tag=dis.readByte();
  short size=dis.readShort();

  byte data[]=new byte[size];

  is.read(data);

  switch(tag) {
   case Component.COMPONENT_Header:
    comp=new Component.Header(name,data);
    break;
   case Component.COMPONENT_Directory:
    comp=new Component.Directory(name,data);
    break;
   case Component.COMPONENT_Applet:
    comp=new Component.Applet(name,data);
    break;
   case Component.COMPONENT_Import:
    comp=new Component.Import(name,data);
    break;
   case Component.COMPONENT_ConstantPool:
    comp=new Component.ConstantPool(name,data);
    break;
   case Component.COMPONENT_Class:
    comp=new Component.Class(name,data);
    break;
   case Component.COMPONENT_Method:
    comp=new Component.Method(name,data);
    break;
   case Component.COMPONENT_StaticField:
    comp=new Component.StaticField(name,data);
    break;
   case Component.COMPONENT_ReferenceLocation:
    comp=new Component.ReferenceLocation(name,data);
    break;
   case Component.COMPONENT_Export:
    comp=new Component.Export(name,data);
    break;
   case Component.COMPONENT_Descriptor:
    comp=new Component.Descriptor(name,data);
    break;
   case Component.COMPONENT_Debug:
    comp=new Component.Debug(name,data);
    break;
  }

  System.out.println("- loaded "+comp+" ["+size+" bytes]");
  return comp;
 }

 public static void put_component(Component comp) {
  components.add(comp);
  lookup.put(new Integer(comp.type()),comp);
 }

 public static Component get_component(int idx) {
  return (Component)components.get(idx);
 }

 public static Component lookup_component(int type) {
  return (Component)lookup.get(new Integer(type));
 }

 public CAPFile(String filename) {
  try {
   components=new ArrayList();
   lookup=new Hashtable();

   File f=new File(filename);

   JarFile jf=new JarFile(f);
   mf=jf.getManifest();

   Enumeration entries=jf.entries();

   while(entries.hasMoreElements()) {
    JarEntry entry=(JarEntry)entries.nextElement();
    String name=entry.getName();

    if (name.endsWith(CAP_EXTENSION)) {
      int size=(int)entry.getSize();
      
      InputStream is=jf.getInputStream(entry);

      Component comp=load_component(name,is);
      put_component(comp);

      is.close();
    }
   }

   for(int i=0;i<load_order.length;i++) {
    Component c=(Component)lookup_component(load_order[i]);
    if (c!=null) c.load();
   }
  } catch(Throwable t) {
   t.printStackTrace();
  }
 }

 private void add_to_jar(JarOutputStream jos,String name,byte data[]) {
  try {
    long time=System.currentTimeMillis();;

    CRC32 crc=new CRC32();
    crc.update(data,0,data.length);

    JarEntry je=new JarEntry(name);
    je.setSize(data.length);
    je.setTime(time);
    je.setCrc(crc.getValue());
    jos.putNextEntry(je);
    jos.write(data,0,data.length);
  } catch(Throwable t) {
   t.printStackTrace();
  }
 }

 public void save(String filename) {
  try {
   FileOutputStream fos=new FileOutputStream(filename);
   JarOutputStream jos=new JarOutputStream(fos,mf);

   for(int i=0;i<components.size();i++) {
    Component comp=(Component)components.get(i);

    ByteArrayOutputStream baos=new ByteArrayOutputStream();
    DataOutputStream dos=new DataOutputStream(baos);

    dos.writeByte(comp.type());
    dos.writeShort(comp.size());
    dos.write(comp.data);

    byte data[]=baos.toByteArray();

    add_to_jar(jos,comp.name(),data);
   }

   jos.close();
   fos.close();
  } catch(Throwable t) {
   t.printStackTrace();
  }
 }
}
