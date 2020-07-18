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

public class EXPFile {

 public static class cp_info {
  public static final byte CONSTANT_Package  = 13;
  public static final byte CONSTANT_Classref = 7;
  public static final byte CONSTANT_Integer  = 3;
  public static final byte CONSTANT_Utf8     = 1;

  public void load(DataInputStream dis) throws Throwable {
  }
 }

 public static class CONSTANT_Package_info extends cp_info {
  byte flags;
  short name_index;
  byte minor_version;
  byte major_version;
  byte aid_length;
  byte aid[];

  public void load(DataInputStream dis) throws Throwable {
   flags=dis.readByte();
   name_index=dis.readShort();
   minor_version=dis.readByte();
   major_version=dis.readByte();
   aid_length=dis.readByte();

   aid=new byte[aid_length];
   dis.read(aid);
  }
 }

 public static class CONSTANT_Classref_info extends cp_info {
  short name_index;

  public void load(DataInputStream dis) throws Throwable {
   name_index=dis.readShort();
  }
 }

 public static class CONSTANT_Integer_info extends cp_info {
  int bytes;

  public void load(DataInputStream dis) throws Throwable {
   bytes=dis.readInt();
  }
 }

 public static class CONSTANT_Utf8_info extends cp_info {
  short length;
  byte bytes[];
  String str;

  public void load(DataInputStream dis) throws Throwable {
   length=dis.readShort();
   bytes=new byte[length];
   dis.read(bytes);

   str=new String(bytes);
  }
 }

 public static class attribute_info {
  short attribute_name_index;
  int attribute_length;
  byte info[];

  public void load(DataInputStream dis) throws Throwable {
   attribute_name_index=dis.readShort();
   attribute_length=dis.readInt();
   
   info=new byte[attribute_length];
   dis.read(info);
  }
 }

 public static class field_info {
  byte token;
  short access_flags;
  short name_index;
  short descriptor_index;
  short attributes_count;
  attribute_info attributes[];

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readShort();
   name_index=dis.readShort();
   descriptor_index=dis.readShort();
   attributes_count=dis.readShort();

   attributes=new attribute_info[attributes_count];

   for(int i=0;i<attributes_count;i++) {
    attributes[i]=new attribute_info();
    attributes[i].load(dis);
   }
   
  }
 }

 public static class method_info {
  byte token;
  short access_flags;
  short name_index;
  short descriptor_index;

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readShort();
   name_index=dis.readShort();
   descriptor_index=dis.readShort();
  }
 }

 public static class class_info {
  byte token;
  short access_flags;
  short name_index;
  short export_supers_count;
  short supers[];
  byte export_interfaces_count;
  short interfaces[];
  short export_fields_count;
  field_info fields[];
  short export_methods_count;
  method_info methods[];

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readShort();
   name_index=dis.readShort();
   export_supers_count=dis.readShort();

   supers=new short[export_supers_count];

   for(int i=0;i<export_supers_count;i++) {
    supers[i]=dis.readShort();
   }

   export_interfaces_count=dis.readByte();

   interfaces=new short[export_interfaces_count];

   for(int i=0;i<export_interfaces_count;i++) {
    interfaces[i]=dis.readShort();
   }   

   export_fields_count=dis.readShort();

   fields=new field_info[export_fields_count];

   for(int i=0;i<export_fields_count;i++) {
    fields[i]=new field_info();
    fields[i].load(dis);
   }

   export_methods_count=dis.readShort();

   methods=new method_info[export_methods_count];

   for(int i=0;i<export_methods_count;i++) {
    methods[i]=new method_info();
    methods[i].load(dis);
   }
  }
 }

 int magic;
 byte minor_version;
 byte major_version;
 short constant_pool_count;
 cp_info constant_pool[];
 short this_package;
 byte export_class_count;
 class_info classes[];

 public void load(DataInputStream dis) throws Throwable {
  magic=dis.readInt();
  minor_version=dis.readByte();
  major_version=dis.readByte();
  constant_pool_count=dis.readShort();

  constant_pool=new cp_info[constant_pool_count];

  for(int i=0;i<constant_pool_count;i++) {
   byte tag=dis.readByte();

   switch(tag) {
    case cp_info.CONSTANT_Package:
     constant_pool[i]=new CONSTANT_Package_info();
     break;
    case cp_info.CONSTANT_Classref:
     constant_pool[i]=new CONSTANT_Classref_info();
     break;
    case cp_info.CONSTANT_Integer:
     constant_pool[i]=new CONSTANT_Integer_info();
     break;
    case cp_info.CONSTANT_Utf8:
     constant_pool[i]=new CONSTANT_Utf8_info();
     break;
   }

   constant_pool[i].load(dis);
  }

  this_package=dis.readShort();
  export_class_count=dis.readByte();

  classes=new class_info[export_class_count];

  for(int i=0;i<export_class_count;i++) {
   classes[i]=new class_info();
   classes[i].load(dis);
  }  
 }

 public int lookup_method_token(String clazz,String name,String descriptor) {
  for(int i=0;i<classes.length;i++) {
   class_info ci=classes[i];

   int cridx=ci.name_index;
   CONSTANT_Classref_info crcpi=(CONSTANT_Classref_info)constant_pool[cridx];

   int cnidx=crcpi.name_index;
   CONSTANT_Utf8_info cncpi=(CONSTANT_Utf8_info)constant_pool[cnidx];

   String cname=cncpi.str;

   if (!cname.equals(clazz)) continue;

   for(int j=0;j<ci.methods.length;j++) {
    method_info mi=ci.methods[j];
   
    int nidx=mi.name_index;
    int didx=mi.descriptor_index;

    CONSTANT_Utf8_info ncpi=(CONSTANT_Utf8_info)constant_pool[nidx];
    CONSTANT_Utf8_info dcpi=(CONSTANT_Utf8_info)constant_pool[didx];

    String cpname=ncpi.str;
    String cpdescriptor=dcpi.str;

    if (name.equals(cpname)&&descriptor.equals(cpdescriptor)) return mi.token;
   }
  }

  return -1;
 }

 public int lookup_class_token(String clazz) {
  for(int i=0;i<classes.length;i++) {
   class_info ci=classes[i];

   int cridx=ci.name_index;
   CONSTANT_Classref_info crcpi=(CONSTANT_Classref_info)constant_pool[cridx];

   int cnidx=crcpi.name_index;
   CONSTANT_Utf8_info cncpi=(CONSTANT_Utf8_info)constant_pool[cnidx];

   String cname=cncpi.str;

   if (cname.equals(clazz)) return ci.token;
  }

  return -1;
 }
 
 public EXPFile(String filename) {
  try {
   FileInputStream fis=new FileInputStream(filename);
   DataInputStream dis=new DataInputStream(fis);

   load(dis);

   dis.close();
   fis.close();
  } catch(Throwable t) {
   t.printStackTrace();
  }
 }

}

