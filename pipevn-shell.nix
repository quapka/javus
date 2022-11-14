{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  name = "my-python-project";
  buildInputs = with pkgs; [
    python310
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
