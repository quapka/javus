{ pkgs ? import <nixpkgs> { } }:
let
  pythonPackages = with pkgs.python310Packages; [
    ipython
    pytest
    plotly
    pandas
    pip
    venvShellHook
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

    pcsclite
    pcsclite.dev
  ] ++ pythonPackages;

  CPATH = with pkgs; "${pcsclite.dev}/include/PCSC";

  LD_LIBRARY_PATH = with pkgs; pkgs.lib.makeLibraryPath [
    pcsclite
    zlib
    libgccjit
  ];

  venvDir = ".virt";
  venvShellHook = ''
    pip install --editable .
  '';

  shellHook = "source ${venvDir}/bin/activate";
}
