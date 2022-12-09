{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  name = "javus";
  buildInputs = with pkgs; [
    python310
    python310Packages.ipython
    python310Packages.pytest
    python310Packages.plotly
    python310Packages.pandas
    pipenv

    ant
    jdk8
    mongodb
    swig
  ];

  LD_LIBRARY_PATH = with pkgs; pkgs.lib.makeLibraryPath [
    pcsclite
    zlib
    libgccjit
  ];
}
