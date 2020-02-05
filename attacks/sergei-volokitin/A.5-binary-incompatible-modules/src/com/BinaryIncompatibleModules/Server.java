/*
 * Copyright 2016 Riscure All rights reserved.
 */
package binaryincompatible.server;

import javacard.framework.*;

/** @aid 0xA0:0x00:0x00:0x00:0xFF:0x10:0x01 */
public class Server {

  /* // The method installed on a card
  public static short[] convertRef ( short[] ref ) {
  return ref;
  }
  */

  public static short[] convertRef(byte[] ref) {
    return null;
  }
}
