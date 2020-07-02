Repository description
----------------------
This repository consists of the code, materials and diploma thesis sources.

### Notation
This `README.md` follows common practices and terminology, but since this project uses multiple technologies and is meant to be cross-platform we provide an explanatory list:
- the dollar symbol `$` used in `the code sections` denotes the prompt of a shell (Bash) on Unix based systems
- the right angle bracket symbol `>` used in `the code sections` denotes the prompt of a Windows command line (`cmd.exe`) or PowerShell (`powershell.exe`)
- the `PROJECT_ROOT` means th topmost/root directory of this project


Diploma thesis topic
--------------------
The current topic of the thesis is: Security analysis of JavaCard Virtual Machine

And the topic description is (in Czech):

Předběžné zadání:
Cílem práce je provést přehled známých útoků na vykonání kódu v rámci virtuálního stroje platformy JavaCard a vytvořit automatizovaný bezpečnostní testovací nástroj analyzující (ne)použitelnost těchto útoků na aktuálních čipových kartách. Útoky mohou být např. založeny na nedokonalé kontrole typů operandů (např. předaných přes Shareable interface), záměrnou modifikací bytecode karetní aplikace před nahráním na kartu nebo nedostatečné separace paměťového prostoru.
Práce pokryje tyto konkrétní kroky:

    Popis provádění kódu aplikace v rámci JavaCard RE a seznam známých bezpečnostních opatření.
    Rešerše publikovaných úroků na JavaCard RE.
    Sběr a spuštění existujících implementací kódu testujících přítomnost potenciálních zranitelností.
    Vytvoření automatizované aplikace pro test (ne)možnosti provádět potenciálně problematické operace.
    Pokus o návrh vlastních útoků na JavaCard RE a jejich případná integrace do testovacího nástroje.
    Vyhodnocení na vybraných reálných kartách.

TODOs
-----
- since each attack will have it's own applet (therefore an AID) we should have a reasonable way of assigning RIDs and PIXs
    - one RID is enough
    - PIX based on type of attack?

- categorize the attacks

General notes from meetings
---------------------------

vynechat Connected
attack using side effects - multiple calls
apdu buffer object
 - write to apdu in one applet and read them in
catching various exceptions

let Petr send the diploma thesis related to the topic

Trello board
- papers: abstracts
- tools

Fresh device setup (Ubuntu 18.04)
------------------
Install `pkcs11-tool` (requires root privileges):
```
$ apt install opensc
```

Install Java:
```
$ apt install openjdk-8-jre-headless
$ apt install openjdk-8-jdk
```

Install Apache build tool:
```
$ apt install ant
```

Install Mongo database:
```
sudo apt install -y mongodb
```

Questions
---------
Can ATR change during card lifetime?
     - Yes.
How to identify card?
    - Custom installed applet?

General notes on a setup
------------------------
In order to manage different versions of JDK use:
$ sudo update-alternatives --config java


Ideas
-----

Define each attack by the APDUs, that are send/receieved

Installation
------------

`pipenv install pkgs/jcvmutils`

Scenario of an individual attack
--------------------------------

steps:
    - [build attacks]
    - [registry attacks]
    - assess states (which applets are installed)
        - get jcversion

    for attack:
        - install applets
            - and veritfy, that they have been added
            - diff
        - run the read mem commands and get their outputs
        - uninstall
        - check differences agains the first state

Testing
-------
If you've got `invoke` installed you can simply run from anywhere within the project:
```
$ inv test
```

[TODO] add paths to the project root before running the tests.
Or with virtual activated run the following:
```
$ pytest -c tests/pytest.ini tests
```

Or outside of the virtual environment run:
```
$ pipenv run pytest -c tests/pytest.ini tests
```

Checking
--------

Runs *checks*, whether the various applets etc. can be build properly,
so that the analysis is ready to be run.
```
pytest -c checks/check.ini checks
```

Development
-----------
In order to be able to manually run and test the updated version (especially the script `jsec`) you need to install the project. You can use `invoke` for that. Run from anywhere in the project:
```
$ inv develop
```
This will install the version under the virtual environment created with Pipenv. If you want to make sure a fresh version is installed (along the saying _have you tried turning it off and on again?_) you can use the flag `--restart`:
```
$ inv develop --restart
```

If you don't have Invoke installed you can perform the previous steps manually. To do so, run the following commands from the project root directory:
```
$ pipenv shell
$ pip3 install --editable .
```
Or together in one command:
```
$ pipenv run pip3 install --editable .
```
To make sure a fresh version is installed you need to uninstall it first:
```
$ pipenv run pip3 uninstall --yes jsec
```


Contribution
------------

https://www.pypa.io/en/latest/code-of-conduct/

# Docker

Using virtualization and containers has become more popular in the recent years
and it is not always for the better as it adds another layer of complexity to
the system. In this case however a lof technologies come together to make this
project possible. To name some of them:

- [PC/SC Smart Card Daemon](https://linux.die.net/man/8/pcscd)- service for communicating with JavaCards
- [GlobalPlatformPro](https://github.com/martinpaljak/GlobalPlatformPro) - command line utility for managing applets (un/installing, sending APDUs) on JavaCards
- [Python3](https://docs.python.org/3.6/) - the main _glue_ for putting it all together
- [pip3](https://docs.python.org/3.6/installing/index.html) - to install Pipenv and other
- [Pipenv](https://github.com/pypa/pipenv) - for managing project's Python dependencies
- [OpenJDK](https://openjdk.java.net/) and [Ant](https://ant.apache.org/) - for building the JavaCard applets
- [ant-javacard](https://github.com/martinpaljak/ant-javacard) - for building the JavaCard applets
- and a few more...

Also, this project is meant to work cross-platform (at least on Linux and Windows)
therefore two different setups would be needed. Those were the main reasons for
containerizing the application. Of course, it is meant as a convenience and 
nothing stops you from using this project natively (for further details see the 
paragraphs about Development).

Using Docker does not simplify everything, because we need to talk directly with
the hardware peripheries (the JavaCards) and now the added virtualization makes 
matters actually worse. The simplest workaround this is making custom entry points
for the different platforms (a Bash script for Linux and PowerShell script for Windows).

Therefore the only requirements for this project are:
- compatible operating system, the project was tested on Ubuntu 18.04 and Windows 10
- physical (external or built-in) reader for JavaCards
- Docker installed (see below for details)
- ability to execute Bash script or Powershell script, respectively.
- _a bit of luck never hurts_
 
inv dock
lsusb
docker run --name test2 -it --device /dev/bus/usb/001/002:/dev/ttyUSB0 jsec

TODO add explanation about why the setup is so complicated.

Currently the project does not have its premade Docker image, that you could simply download and execute. However, you can clone the project and build a local Docker image.


## On windows

### Installing Docker

In case you don't have Docker already installed it is not very difficult. As usual, you need to go through the common steps of downloading and installing this software. At the time of writing the latest information on how to do that are at https://docs.docker.com/docker-for-windows/install/.

### Building the Docker image

In order to build the Docker image locally you need to execute the following command in the `PROJECT_ROOT` either in `cmd` or PowerShell
```
> docker build --tag jsec .
```

The name `jsec` is required in case you want to use the tooling explained in the
following sections, because it will be used to start the right Docker container.
The `build` command takes a while (several minutes), because a lot needs to be set up. Therefore,
it is a good place to take a break and sip a coffee.



## Development

As the initial development was done under Linux the setup will be explained only 
n this environment. It is in general possible to overcome this by creating slightly
altered Docker image, that won't have this application as the entry point, but will
allow to enter the Shell and make the necessary changes from there.

- Make sure to `pip3 install --upgrade pipenv` to run the latest Pipenv
- Install `jsecdev`

Fix GlobalPlatformPro to version:
2d4bb36c145bd8c13606f12aa14e6e29d8ecef78
Docker
sudo apt install maven
