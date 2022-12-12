{ pkgs ? import <nixpkgs> { } }:
let
  pythonPackages = with pkgs.python310Packages; [
    ipython
    pytest
    plotly
    pandas
    jupyter
    jupytext
  ];
in
pkgs.mkShell rec {
  name = "javus";

  buildInputs = with pkgs; [
    python310
    pipenv

    ant
    jdk8
    mongodb
    swig
  ] ++ pythonPackages;

  LD_LIBRARY_PATH = with pkgs; pkgs.lib.makeLibraryPath [
    pcsclite
    zlib
    libgccjit
  ];
}
