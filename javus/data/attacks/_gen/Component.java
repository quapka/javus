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
import java.io.*;
import java.util.*;

public class Component {
 public static final int COMPONENT_Header            = 1;
 public static final int COMPONENT_Directory         = 2;
 public static final int COMPONENT_Applet            = 3;
 public static final int COMPONENT_Import            = 4;
 public static final int COMPONENT_ConstantPool      = 5;
 public static final int COMPONENT_Class             = 6;
 public static final int COMPONENT_Method            = 7;
 public static final int COMPONENT_StaticField       = 8;
 public static final int COMPONENT_ReferenceLocation = 9;
 public static final int COMPONENT_Export            = 10;
 public static final int COMPONENT_Descriptor        = 11;
 public static final int COMPONENT_Debug             = 12;

 public static class package_info {
  byte minor_version;
  byte major_version;
  byte AID_length;
  byte AID[];

  public void load(DataInputStream dis) throws Throwable {
   minor_version=dis.readByte();
   major_version=dis.readByte();
   AID_length=dis.readByte();

   AID=new byte[AID_length];
   dis.read(AID);
  }
 }

 public static class package_name_info {
  byte name_length;
  byte name[];

  public void load(DataInputStream dis) throws Throwable {
   name_length=dis.readByte();

   name=new byte[name_length];
   dis.read(name);
  }
 }

 public static class Header extends Component {
  public static final byte ACC_INT    = 0x01;
  public static final byte ACC_EXPORT = 0x02;
  public static final byte ACC_APPLET = 0x04;

  int magic;
  byte minor_version;
  byte major_version;
  byte flags;
  package_info pckage;
  package_name_info package_name;

  public void load(DataInputStream dis) throws Throwable {
   magic=dis.readInt();
   minor_version=dis.readByte();
   major_version=dis.readByte();
   flags=dis.readByte();

   pckage=new package_info();
   pckage.load(dis);

   CAPFile.minor_version=minor_version;

   if (CAPFile.minor_version==2) {
    package_name=new package_name_info();
    package_name.load(dis);
   }
  }

  public Header(String name,byte data[]) {
   super(name,COMPONENT_Header,data);
  }
 }

 public static class static_field_size_info {
  short image_size;
  short array_init_count;
  short array_init_size;

  public void load(DataInputStream dis) throws Throwable {
   image_size=dis.readShort();
   array_init_count=dis.readShort();
   array_init_size=dis.readShort();
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeShort(image_size);
   dos.writeShort(array_init_count);
   dos.writeShort(array_init_size);
  }
 }

 public static class custom_component_info {
  byte AID_length;
  byte AID[];

  public void load(DataInputStream dis) throws Throwable {
   AID_length=dis.readByte();

   AID=new byte[AID_length];
   dis.read(AID);
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(AID.length);

   dos.write(AID);
  }
 }

 public static class Directory extends Component {
  short component_sizes[];
  static_field_size_info static_field_size;
  byte import_count;
  byte applet_count;
  byte custom_count;
  custom_component_info custom_components[];

  public void load(DataInputStream dis) throws Throwable {
   component_sizes=new short[CAPFile.minor_version==2 ? 12:11];

   for(int i=0;i<component_sizes.length;i++) {
    component_sizes[i]=dis.readShort();
   }

   static_field_size=new static_field_size_info();
   static_field_size.load(dis);

   import_count=dis.readByte();
   applet_count=dis.readByte();
   custom_count=dis.readByte();

   custom_components=new custom_component_info[custom_count];

   for(int i=0;i<custom_count;i++) {
    custom_components[i]=new custom_component_info();
    custom_components[i].load(dis);  
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   for(int i=0;i<component_sizes.length;i++) {
    dos.writeShort(component_sizes[i]);
   }

   static_field_size.save(dos);

   dos.writeByte(import_count);
   dos.writeByte(applet_count);
   dos.writeByte(custom_count);

   for(int i=0;i<custom_components.length;i++) {
    custom_components[i].save(dos);  
   }
  }

  public Directory(String name,byte data[]) {
   super(name,COMPONENT_Directory,data);
  }
 }

 public static class applet_info {
  byte AID_length;
  byte AID[];
  short install_method_offset;

  public void load(DataInputStream dis) throws Throwable {
   AID_length=dis.readByte();

   AID=new byte[AID_length];
   dis.read(AID);

   install_method_offset=dis.readShort();
  }
 }

 public static class Applet extends Component {
  byte count;
  applet_info applets[];

  public void load(DataInputStream dis) throws Throwable {
   count=dis.readByte();

   applets=new applet_info[count];

   for(int i=0;i<count;i++) {
    applets[i]=new applet_info();
    applets[i].load(dis);    
   }
  }

  public Applet(String name,byte data[]) {
   super(name,COMPONENT_Applet,data);
  }
 }

 public static class Import extends Component {
  byte count;
  package_info packages[];

  public void load(DataInputStream dis) throws Throwable {
   count=dis.readByte();

   packages=new package_info[count];

   for(int i=0;i<count;i++) {
    packages[i]=new package_info();
    packages[i].load(dis);
   }
  }

  public Import(String name,byte data[]) {
   super(name,COMPONENT_Import,data);
  }
 }

 public static final byte CONSTANT_Classref         = 1;
 public static final byte CONSTANT_InstanceFieldref = 2;
 public static final byte CONSTANT_VirtualMethodref = 3;
 public static final byte CONSTANT_SuperMethodref   = 4;
 public static final byte CONSTANT_StaticFieldref   = 5;
 public static final byte CONSTANT_StaticMethodref  = 6;

 public static class CPRef {
  public void load(DataInputStream dis) throws Throwable {
  }

  public void save(DataOutputStream dos) throws Throwable {
  }
 }

 public static class class_ref {
  boolean internal;
  short internal_class_ref;
  byte package_token;
  byte class_token;

  public void load(DataInputStream dis) throws Throwable {
   internal_class_ref=dis.readShort();
   internal=true;

   if ((internal_class_ref&0x8000)!=0) {
    internal=false;
    package_token=(byte)((internal_class_ref>>8)&0x7f);
    class_token=(byte)((internal_class_ref)&0xff);
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeShort(internal_class_ref);
  }
 }

 public static class Classref extends CPRef {
  class_ref cref;
  byte padding;

  public void load(DataInputStream dis) throws Throwable {
   cref=new class_ref();
   cref.load(dis);

   padding=dis.readByte();
  }

  public void save(DataOutputStream dos) throws Throwable {
   cref.save(dos);
   dos.writeByte(padding);
  }
 }

 public static class InstanceFieldref extends CPRef {
  class_ref clazz;
  byte token;

  public void load(DataInputStream dis) throws Throwable {
   clazz=new class_ref();
   clazz.load(dis);

   token=dis.readByte();
  }

  public void save(DataOutputStream dos) throws Throwable {
   clazz.save(dos);
   dos.writeByte(token);
  }
 }

 public static class VirtualMethodref extends CPRef {
  class_ref clazz;
  byte token;

  public void load(DataInputStream dis) throws Throwable {
   clazz=new class_ref();
   clazz.load(dis);

   token=dis.readByte();
  }

  public void save(DataOutputStream dos) throws Throwable {
   clazz.save(dos);
   dos.writeByte(token);
  }
 }

 public static class SuperMethodref extends CPRef {
  class_ref clazz;
  byte token;

  public void load(DataInputStream dis) throws Throwable {
   clazz=new class_ref();
   clazz.load(dis);

   token=dis.readByte();
  }

  public void save(DataOutputStream dos) throws Throwable {
   clazz.save(dos);
   dos.writeByte(token);
  }
 }

 public static class StaticFieldref extends CPRef {
  boolean internal;

  byte padding;
  short offset;

  byte package_token;
  byte class_token;
  byte token;
  
  public void load(DataInputStream dis) throws Throwable {
   package_token=dis.readByte();

   if (package_token==0) {
    internal=true;
    offset=dis.readShort();
   } else {
    internal=false;
    class_token=dis.readByte();
    token=dis.readByte();
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(package_token);

   if (package_token==0) {
    dos.writeShort(offset);
   } else {
    dos.writeByte(class_token);
    dos.writeByte(token);
   }
  }
 }

 public static class StaticMethodref extends CPRef {
  boolean internal;

  byte padding;
  short offset;

  byte package_token;
  byte class_token;
  byte token;
  
  public void load(DataInputStream dis) throws Throwable {
   package_token=dis.readByte();

   if (package_token==0) {
    internal=true;
    offset=dis.readShort();
   } else {
    internal=false;
    class_token=dis.readByte();
    token=dis.readByte();
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(package_token);

   if (package_token==0) {
    dos.writeShort(offset);
   } else {
    dos.writeByte(class_token);
    dos.writeByte(token);
   }
  }
 }

 public static class cp_info {
  byte tag;
  CPRef ref;

  public void load(DataInputStream dis) throws Throwable {
   tag=dis.readByte();

   switch(tag) {
    case CONSTANT_Classref:
     ref=new Classref();
     ref.load(dis);
     break;
    case CONSTANT_InstanceFieldref:
     ref=new InstanceFieldref();
     ref.load(dis);
     break;
    case CONSTANT_VirtualMethodref:
     ref=new VirtualMethodref();
     ref.load(dis);
     break;
    case CONSTANT_SuperMethodref:
     ref=new SuperMethodref();
     ref.load(dis);
     break;
    case CONSTANT_StaticFieldref:
     ref=new StaticFieldref();
     ref.load(dis);
     break;
    case CONSTANT_StaticMethodref:
     ref=new StaticMethodref();
     ref.load(dis);
     break;
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(tag);
   ref.save(dos);
  }
 };

 public static class ConstantPool extends Component {
  short count;
  cp_info constant_pool[];

  public void load(DataInputStream dis) throws Throwable {
   count=dis.readShort();

   constant_pool=new cp_info[count];

   for(int i=0;i<count;i++) {
    constant_pool[i]=new cp_info();
    constant_pool[i].load(dis);
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeShort(constant_pool.length);

   for(int i=0;i<constant_pool.length;i++) {
    constant_pool[i].save(dos);
   }
  }

  public ConstantPool(String name,byte data[]) {
   super(name,COMPONENT_ConstantPool,data);
  }
 }

 public static class type_descriptor {
  byte nibble_count;
  byte type[];

  public void load(DataInputStream dis) throws Throwable {
   nibble_count=dis.readByte();
   type=new byte[(nibble_count+1)/2];
   dis.read(type);
  } 

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(nibble_count);
   dos.write(type);
  }

  public int size() {
   return type.length+1;
  }
 }

 public static class interface_name_info {
  byte interface_name_length;
  byte interface_name[];

  public void load(DataInputStream dis) throws Throwable {
   interface_name_length=dis.readByte();
   interface_name=new byte[interface_name_length];

   dis.read(interface_name);
  }
 }

 public static class interface_info {
  public static final byte ACC_INTERFACE = 0x8;
  public static final byte ACC_SHAREABLE = 0x4;
  public static final byte ACC_REMOTE    = 0x2;

  byte flags;
  byte interface_count;
  class_ref superinterfaces[];
  interface_name_info interface_name;

  public interface_info(byte flags,byte interface_count) {
   this.flags=flags;
   this.interface_count=interface_count;
  }

  public void load(DataInputStream dis) throws Throwable {
   superinterfaces=new class_ref[interface_count];   

   for(int i=0;i<interface_count;i++) {
    superinterfaces[i]=new class_ref();
    superinterfaces[i].load(dis);
   }

   if ((flags&ACC_REMOTE)!=0) {
    interface_name=new interface_name_info();
    interface_name.load(dis);    
   }
  }
 }

 public static class implemented_interface_info {
  class_ref intface;
  byte count;
  byte index[];

  public void load(DataInputStream dis) throws Throwable {
   intface=new class_ref();
   intface.load(dis);

   count=dis.readByte();

   index=new byte[count];
   dis.read(index);   
  }  
 }

 public static class remote_method_info {
  short remote_method_hash;
  short signature_offset;
  short virtual_method_token;

  public void load(DataInputStream dis) throws Throwable {
   remote_method_hash=dis.readShort();
   signature_offset=dis.readShort();
   virtual_method_token=dis.readShort();
  }
 }

 public static class remote_interface_info {
  byte remote_methods_count;
  remote_method_info remote_methods[];
  byte hash_modifier_length;
  byte hash_modifier[];
  byte class_name_length;
  byte class_name[];
  byte remote_interfaces_count;
  class_ref remote_interfaces[];

  public void load(DataInputStream dis) throws Throwable {
   remote_methods_count=dis.readByte();
   remote_methods=new remote_method_info[remote_methods_count];

   for(int i=0;i<remote_methods_count;i++) {
    remote_methods[i]=new remote_method_info();
    remote_methods[i].load(dis);
   }

   hash_modifier_length=dis.readByte();
   hash_modifier=new byte[hash_modifier_length];
   dis.read(hash_modifier);

   class_name_length=dis.readByte();
   class_name=new byte[class_name_length];
   dis.read(class_name);

   remote_interfaces_count=dis.readByte();
   remote_interfaces=new class_ref[remote_interfaces_count];

   for(int i=0;i<remote_interfaces_count;i++) {
    remote_interfaces[i]=new class_ref();
    remote_interfaces[i].load(dis);
   }
  }
 }

 public static class class_info {
  public static final byte ACC_INTERFACE = 0x8;
  public static final byte ACC_SHAREABLE = 0x4;
  public static final byte ACC_REMOTE    = 0x2;

  byte flags;
  byte interface_count;
  class_ref super_class_ref;
  byte declared_instance_size;
  byte first_reference_token;
  byte reference_count;
  byte public_method_table_base;
  byte public_method_table_count;
  byte package_method_table_base;
  byte package_method_table_count;
  short public_virtual_method_table[];
  short package_virtual_method_table[];
  implemented_interface_info interfaces[];
  remote_interface_info remote_interfaces;

  public class_info(byte flags,byte interface_count) {
   this.flags=flags;
   this.interface_count=interface_count;
  }

  public void load(DataInputStream dis) throws Throwable {
   super_class_ref=new class_ref();
   super_class_ref.load(dis);

   declared_instance_size=dis.readByte();

   first_reference_token=dis.readByte();
   reference_count=dis.readByte();
   public_method_table_base=dis.readByte();
   public_method_table_count=dis.readByte();
   package_method_table_base=dis.readByte();
   package_method_table_count=dis.readByte();

   public_virtual_method_table=new short[public_method_table_count];
   package_virtual_method_table=new short[package_method_table_count];

   for(int i=0;i<public_method_table_count;i++) {
    public_virtual_method_table[i]=dis.readShort();
   }

   for(int i=0;i<package_method_table_count;i++) {
    package_virtual_method_table[i]=dis.readShort();
   }

   interfaces=new implemented_interface_info[interface_count];

   for(int i=0;i<interface_count;i++) {
    interfaces[i]=new implemented_interface_info();
    interfaces[i].load(dis);
   }

   if ((flags&ACC_REMOTE)!=0) {
    remote_interfaces=new remote_interface_info();
    remote_interfaces.load(dis);
   }
  }
 }

 public static class Class extends Component {
  short signature_pool_length;
  type_descriptor signature_pool[];
  interface_info interfaces[];
  class_info classes[];

  public void load(DataInputStream dis) throws Throwable {
   int size=0;

   if (CAPFile.minor_version==2) {
    signature_pool_length=dis.readShort();

    ArrayList types=new ArrayList();

    while(size<signature_pool_length) {
     type_descriptor type=new type_descriptor();
     type.load(dis);

     types.add(type);
     size+=type.size();   
    }

    signature_pool=new type_descriptor[types.size()];

    for(int i=0;i<types.size();i++) {
     signature_pool[i]=(type_descriptor)types.get(i);
    }
   }

   ArrayList intlist=new ArrayList();
   ArrayList classlist=new ArrayList();

   byte flags=0;
   byte interface_count=0;

   while(dis.available()>0) {
    byte b=dis.readByte();

    flags=(byte)((b>>4)&0x0f);
    interface_count=(byte)((b)&0x0f);

    if ((flags&class_info.ACC_INTERFACE)!=0) {
     interface_info intface=new interface_info(flags,interface_count);
     intface.load(dis);    
     intlist.add(intface);
    } else {
     class_info clazz=new class_info(flags,interface_count);
     clazz.load(dis);    
     classlist.add(clazz);
    } 
   } 

   interfaces=new interface_info[intlist.size()];
   classes=new class_info[classlist.size()];

   for(int i=0;i<intlist.size();i++) {
    interfaces[i]=(interface_info)intlist.get(i);
   }   
      
   for(int i=0;i<classlist.size();i++) {
    classes[i]=(class_info)classlist.get(i);
   }   

  }

  public Class(String name,byte data[]) {
   super(name,COMPONENT_Class,data);
  }
 }

 public static class exception_handler_info {
  short start_offset;
  short active_length;
  short handler_offset;
  short catch_type_index;

  public void load(DataInputStream dis) throws Throwable {
   start_offset=dis.readShort();
   active_length=dis.readShort();
   handler_offset=dis.readShort();
   catch_type_index=dis.readShort();
  }
 }

 public static class method_info {
  method_header_info method_header;
  method_descriptor_info mdi;
  int size;
  short bytecode_size;
  int bytecode_off;
  byte bytecodes[];

  public method_info(int size,short bytecode_size,method_descriptor_info mdi) {
   this.size=size;
   this.bytecode_size=bytecode_size;
   this.mdi=mdi;
  }

  public void load(DataInputStream dis) throws Throwable {
   method_header=new method_header_info();
   method_header.load(dis);

   bytecode_off=size-dis.available();

   bytecodes=new byte[bytecode_size];
   dis.read(bytecodes);
  }
 }

 public static class method_header_info {
  public static final byte ACC_EXTENDED = 0x8;
  public static final byte ACC_ABSTRACT = 0x4;

  byte flags;
  byte max_stack;
  byte nargs;
  byte max_locals;

  public void load(DataInputStream dis) throws Throwable {
   byte b=dis.readByte();

   flags=(byte)((b>>4)&0x0f);

   if ((flags&ACC_EXTENDED)!=0) {
    max_stack=dis.readByte();
    nargs=dis.readByte();
    max_locals=dis.readByte();
   } else {
    max_stack=(byte)((b)&0x0f);

    b=dis.readByte();

    nargs=(byte)((b>>4)&0x0f);
    max_locals=(byte)((b)&0x0f);    
   }
  }
 }

 public static class Method extends Component {
  byte handler_count;
  exception_handler_info exception_handlers[];
  method_info methods[];

  public void load(DataInputStream dis) throws Throwable {
   handler_count=dis.readByte();

   exception_handlers=new exception_handler_info[handler_count];

   for(int i=0;i<handler_count;i++) {
    exception_handlers[i]=new exception_handler_info();
    exception_handlers[i].load(dis);
   }       

   ArrayList methlist=new ArrayList();

   while(dis.available()>0) {
    int off=size-dis.available();

    Descriptor desc=(Descriptor)CAPFile.lookup_component(COMPONENT_Descriptor);
    method_descriptor_info mdi=desc.lookup_method((short)off);    

    method_info mi=new method_info(size,mdi.bytecode_count,mdi);
    mi.load(dis);

    methlist.add(mi);
   }  

   methods=new method_info[methlist.size()];
   
   for(int i=0;i<methlist.size();i++) {
    methods[i]=(method_info)methlist.get(i);
   }
  }

  public Method(String name,byte data[]) {
   super(name,COMPONENT_Method,data);
  }
 }

 public static class array_init_info {
  byte type;
  short count;
  byte values[];

  public void load(DataInputStream dis) throws Throwable {
   type=dis.readByte();
   count=dis.readShort();

   values=new byte[count];
   dis.read(values);
  }
 }

 public static class StaticField extends Component {
  short image_size;
  short reference_count;
  short array_init_count;
  array_init_info array_init[];
  short default_value_count;
  short non_default_value_count;
  byte non_default_values[];

  public void load(DataInputStream dis) throws Throwable {
   image_size=dis.readShort();
   reference_count=dis.readShort();
   array_init_count=dis.readShort();

   array_init=new array_init_info[array_init_count];
   for(int i=0;i<array_init_count;i++) {
    array_init[i]=new array_init_info();
    array_init[i].load(dis);
   }

   default_value_count=dis.readShort();
   non_default_value_count=dis.readShort();

   non_default_values=new byte[non_default_value_count];
   dis.read(non_default_values);   
  }

  public StaticField(String name,byte data[]) {
   super(name,COMPONENT_StaticField,data);
  }
 }

 public static class ReferenceLocation extends Component {
  short byte_index_count;
  byte offsets_to_byte_indices[];
  short byte2_index_count;
  byte offsets_to_byte2_indices[];

  public void load(DataInputStream dis) throws Throwable {
   byte_index_count=dis.readShort();

   offsets_to_byte_indices=new byte[byte_index_count];   
   dis.read(offsets_to_byte_indices);

   byte2_index_count=dis.readShort();

   offsets_to_byte2_indices=new byte[byte2_index_count];   
   dis.read(offsets_to_byte2_indices);   
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeShort(offsets_to_byte_indices.length);
   dos.write(offsets_to_byte_indices);

   dos.writeShort(offsets_to_byte2_indices.length);
   dos.write(offsets_to_byte2_indices);
  }

  public ReferenceLocation(String name,byte data[]) {
   super(name,COMPONENT_ReferenceLocation,data);
  }
 }

 public static class class_export_info {
  short class_offset;
  byte static_field_count;
  byte static_method_count;
  short static_field_offsets[];
  short static_method_offsets[];

  public void load(DataInputStream dis) throws Throwable {
   class_offset=dis.readShort();
   static_field_count=dis.readByte();
   static_method_count=dis.readByte();

   static_field_offsets=new short[static_field_count];

   for(int i=0;i<static_field_count;i++) {
    static_field_offsets[i]=dis.readShort();
   }

   static_method_offsets=new short[static_method_count];

   for(int i=0;i<static_method_count;i++) {
    static_method_offsets[i]=dis.readShort();
   }
  }
 }

 public static class Export extends Component {
  byte class_count;
  class_export_info class_exports[];

  public void load(DataInputStream dis) throws Throwable {
   class_count=dis.readByte();
    
   class_exports=new class_export_info[class_count];

   for(int i=0;i<class_count;i++) {
    class_exports[i]=new class_export_info();
    class_exports[i].load(dis);
   }
  }

  public Export(String name,byte data[]) {
   super(name,COMPONENT_Export,data);
  }
 }

 public static class field_descriptor_info {
  public static final byte ACC_PUBLIC    = 0x01;
  public static final byte ACC_PRIVATE   = 0x02;
  public static final byte ACC_PROTECTED = 0x04;
  public static final byte ACC_STATIC    = 0x08;
  public static final byte ACC_FINAL     = 0x10;

  byte token;
  byte access_flags;

  StaticFieldref static_field;
  class_ref ref_clazz;
  byte ref_token;

  short type;

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readByte();

   if ((access_flags&ACC_STATIC)!=0) {
    static_field=new StaticFieldref();
    static_field.load(dis);    
   } else {
    ref_clazz=new class_ref();
    ref_clazz.load(dis);

    ref_token=dis.readByte();
   }

   type=dis.readShort();   
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(token);
   dos.writeByte(access_flags);

   if ((access_flags&ACC_STATIC)!=0) {
    static_field.save(dos);    
   } else {
    ref_clazz.save(dos);

    dos.writeByte(ref_token);
   }

   dos.writeShort(type);
  }
 }

 public static class method_descriptor_info {
  public static final int ACC_PUBLIC    = 0x01;
  public static final int ACC_PRIVATE   = 0x02;
  public static final int ACC_PROTECTED = 0x04;
  public static final int ACC_STATIC    = 0x08;
  public static final int ACC_FINAL     = 0x10;
  public static final int ACC_ABSTRACT  = 0x40;
  public static final int ACC_INIT      = 0x80;

  byte token;
  byte access_flags;
  short method_offset;
  short type_offset;
  short bytecode_count;
  short exception_handler_count;
  short exception_handler_index;

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readByte();

   method_offset=dis.readShort();
   type_offset=dis.readShort();

   bytecode_count=dis.readShort();
   exception_handler_count=dis.readShort();
   exception_handler_index=dis.readShort();
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(token);
   dos.writeByte(access_flags);

   dos.writeShort(method_offset);
   dos.writeShort(type_offset);

   dos.writeShort(bytecode_count);
   dos.writeShort(exception_handler_count);
   dos.writeShort(exception_handler_index);
  }
 }

 public static class class_descriptor_info {
  public static final int ACC_PUBLIC    = 0x01;
  public static final int ACC_FINAL     = 0x10;
  public static final int ACC_INTERFACE = 0x40;
  public static final int ACC_ABSTRACT  = 0x80;

  byte token;
  byte access_flags;
  class_ref this_class_ref;
  byte interface_count;
  short field_count;
  short method_count;
  class_ref interfaces[];
  field_descriptor_info fields[];
  method_descriptor_info methods[];

  public void load(DataInputStream dis) throws Throwable {
   token=dis.readByte();
   access_flags=dis.readByte();
   
   this_class_ref=new class_ref();
   this_class_ref.load(dis);

   interface_count=dis.readByte();
   field_count=dis.readShort();
   method_count=dis.readShort();

   interfaces=new class_ref[interface_count];

   for(int i=0;i<interface_count;i++) {
    interfaces[i]=new class_ref();
    interfaces[i].load(dis);
   }

   fields=new field_descriptor_info[field_count];

   for(int i=0;i<field_count;i++) {
    fields[i]=new field_descriptor_info();
    fields[i].load(dis);
   }

   methods=new method_descriptor_info[method_count];

   for(int i=0;i<method_count;i++) {
    methods[i]=new method_descriptor_info();
    methods[i].load(dis);
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(token);
   dos.writeByte(access_flags);
   
   this_class_ref.save(dos);

   dos.writeByte(interfaces.length);
   dos.writeShort(fields.length);
   dos.writeShort(methods.length);

   for(int i=0;i<interfaces.length;i++) {
    interfaces[i].save(dos);
   }

   for(int i=0;i<fields.length;i++) {
    fields[i].save(dos);
   }

   for(int i=0;i<methods.length;i++) {
    methods[i].save(dos);
   }
  }
 }

 public static class type_descriptor_info {
  short constant_pool_count;
  short constant_pool_types[];
  type_descriptor type_desc[];

  public void load(DataInputStream dis) throws Throwable {
   constant_pool_count=dis.readShort();
   constant_pool_types=new short[constant_pool_count];
  
   for(int i=0;i<constant_pool_count;i++) {
    constant_pool_types[i]=dis.readShort();
   }
   
   ArrayList types=new ArrayList();
   
   while(dis.available()>0) {
    type_descriptor type=new type_descriptor();
    type.load(dis);

    types.add(type);
   }

   type_desc=new type_descriptor[types.size()];

   for(int i=0;i<types.size();i++) {
    type_desc[i]=(type_descriptor)types.get(i);
   }
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeShort(constant_pool_count);
  
   for(int i=0;i<constant_pool_types.length;i++) {
    dos.writeShort(constant_pool_types[i]);
   }
   
   for(int i=0;i<type_desc.length;i++) {
    type_desc[i].save(dos);
   }
  }
 }

 public static class Descriptor extends Component {
  byte class_count;
  class_descriptor_info classes[];
  type_descriptor_info types;

  public void load(DataInputStream dis) throws Throwable {
   class_count=dis.readByte();

   classes=new class_descriptor_info[class_count];

   for(int i=0;i<class_count;i++) {
    classes[i]=new class_descriptor_info();
    classes[i].load(dis);
   }

   types=new type_descriptor_info();
   types.load(dis);
  }

  public void save(DataOutputStream dos) throws Throwable {
   dos.writeByte(class_count);

   for(int i=0;i<classes.length;i++) {
    classes[i].save(dos);
   }

   types.save(dos);
  }

  public method_descriptor_info lookup_method(short off) {
   for(int i=0;i<classes.length;i++) {
    class_descriptor_info cdi=classes[i];

    for(int j=0;j<cdi.methods.length;j++) {
     method_descriptor_info mdi=cdi.methods[j];

     if (mdi.method_offset==off) return mdi;
    }
   }

   return null;
  }

  public Descriptor(String name,byte data[]) {
   super(name,COMPONENT_Descriptor,data);
  }
 }

 public static class Debug extends Component {
  public Debug(String name,byte data[]) {
   super(name,COMPONENT_Debug,data);
  }
 }

 String name;
 byte data[];

 byte type;
 short size;

 public void load() throws Throwable {
  ByteArrayInputStream bais=new ByteArrayInputStream(data);
  DataInputStream dis=new DataInputStream(bais);
  load(dis);
 }

 public void load(DataInputStream dis) throws Throwable {
 }

 public void sync() {
  try {
   ByteArrayOutputStream baos=new ByteArrayOutputStream();
   DataOutputStream dos=new DataOutputStream(baos);

   save(dos);

   data=baos.toByteArray();
   size=(short)data.length;
  } catch(Throwable t) {}
 }

 public void save(DataOutputStream dos) throws Throwable {
 }

 public Component(String name,int tag,byte data[]) {
  try {
   this.name=name;
   this.data=data;

   this.type=(byte)tag;
   this.size=(short)data.length;
  } catch(Throwable t) {
   t.printStackTrace();
  }
 }

 public byte type() {
  return type;
 }

 public short size() {
  return size;
 }

 public String name() {
  return name;
 }

 public byte[] data() {
  return data;
 }

}
