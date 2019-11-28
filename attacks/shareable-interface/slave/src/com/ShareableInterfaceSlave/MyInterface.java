package com.shareableinterfaceslave;

import javacard.framework.*;

public interface MyInterface extends Shareable {
  public byte[] giveArray();

  public void accessArray(byte[] myArray); // Slave assumes byte[]

  public void test();
}
