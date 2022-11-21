{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  name = "my-python-project";
  buildInputs = with pkgs; [
    python310
    python310Packages.ipython
    python310Packages.pytest
    pipenv

    ant
    jdk8
    mongodb
    swig
  ];

  LD_LIBRARY_PATH = with pkgs; pkgs.lib.makeLibraryPath [
    pcsclite
  ];
}
