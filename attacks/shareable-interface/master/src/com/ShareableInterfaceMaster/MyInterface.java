package com.shareableinterfacemaster;

import javacard.framework.*;

public interface MyInterface extends Shareable {
  public byte[] giveArray();

  public void accessArray(short[] myArray); // Master assumes byte[]

  public void test();
}
