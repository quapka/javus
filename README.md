JavaCard Vulnerability Scanner
------------------------------

As part of a master's thesis at the Faculty of Informatics at Masaryk University
I have developed a testing framework for executing known logical attacks against
the JavaCard platform. This tool is made public and will be further developed,
especially if the JavaCard community will find it useful.

The useful information for now are:
```
[DISCLAIMER] Running the analysis can potentially dammage (brick/lock) your card!
By using this tool you acknowledge this fact and use the tool at your on risk.
This tool is meant to be used for analysis and research on spare JavaCards in order
to infer something about the level of the security of the JavaCard Virtual Machine
implementation it is running.
```

This is **NOT** a joke! This tool contains real attacks. The goal of this project
is to learn about the security of various JavaCard.

Project structure
-----------------

The main entrypoint is in `scripts/javus`. However, it has several dependencies.
A bootstraping script `bin/boostrap-ubuntu-18.04.sh` exists for the purpose of
setting up the machine.

After card is inserted the tool can be invoked by:
```
$ javus run
```
Again, you are running this tool at your own risk.

Licensing
---------

The code related to the framework itself is MIT licensed. However, some of the POCs (namely, those from [Security Explorations](http://www.security-explorations.com/javacard_details.html)) have different license. Therefore using code from this repository should be done with care -- if in doubt, add an issue and ask the authors. More details are [here](https://github.com/quapka/javus/tree/master/javus/data/attacks).
