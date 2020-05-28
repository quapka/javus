Repository description
----------------------
This repository consists of the code, materials and diploma thesis sources.

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
