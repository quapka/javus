/** Copyright 2016 Riscure */
package class_type_conf.lib;

import class_type_conf.c1.C1;
import class_type_conf.c2.C2;
import javacard.framework.*;

/**
 * @aid 0xA0:0x00:0x00:0x00:0x00:0x66:0x01
 * @version 1.0
 */
public class LibC { // binary incompatible library
  /*
  public static C1 convRef(C1 c1i) { //this method should be present on a card

      return c1i;
  }*/

  public static C1 convRef(C2 c2i) {
    C1 cc = new C1();
    return cc;
  }
}
