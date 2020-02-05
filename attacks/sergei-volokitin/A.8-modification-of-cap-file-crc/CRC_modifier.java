/*
 * Modifies CRC codes of a corrupted CAP file.
 * Copyright 2016 Riscure All rights reserved.
 */

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.util.Enumeration;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import java.util.jar.JarOutputStream;
import java.util.zip.CRC32;
import java.util.zip.Checksum;

public class CRC_modifier {

  public static void main(String[] args) throws Exception {
    JarFile jarInFile = new JarFile(args[0]);
    File jarOutFile = new File(args[1]);
    recomputeCRC(jarInFile, jarOutFile);
    return;
  }

  public static void recomputeCRC(JarFile jarInFile, File jarOutFile) throws Exception {
    int bytesRead;
    int tmp = 0;
    InputStream is;
    byte[] buffer = new byte[4096]; // buffer to copy content of the files
    JarOutputStream jarOutStream = new JarOutputStream(new FileOutputStream(jarOutFile));

    Enumeration<JarEntry> e = jarInFile.entries();

    while (e.hasMoreElements()) {
      JarEntry je = (JarEntry) e.nextElement();
      String name = je.getName();
      long crc = je.getCrc();

      JarEntry nje = new JarEntry(name);
      nje.setMethod(JarOutputStream.STORED);

      is = jarInFile.getInputStream(je);
      bytesRead = 0;

      Checksum checksum = new CRC32();

      while ((tmp = is.read(buffer)) != -1) {
        checksum.update(buffer, 0, tmp);
        bytesRead += tmp;
      }
      long crcVal = checksum.getValue();
      nje.setCrc(crcVal);
      nje.setSize(bytesRead);
      if (je.getCrc() != nje.getCrc()) {
        System.out.println("CRC of " + je.getName() + " recomputed.");
      }
      jarOutStream.putNextEntry(nje);
      is = jarInFile.getInputStream(je);

      // copying of the content of the entry
      bytesRead = 0;
      while ((bytesRead = is.read(buffer)) != -1) {
        jarOutStream.write(buffer, 0, bytesRead);
      }
      is.close();
      jarOutStream.flush();
      jarOutStream.closeEntry();
    }
    jarOutStream.close();
  }
}
