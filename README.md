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


Usage
-----

Clone this repository by running:
```
$ git clone git@github.com:quapka/javus.git
```

### Run `javus` natively on Linux

In order to run `javus` natively on Linux you need additional dependencies. You can use `bin/boostrap-ubuntu-18.04.sh` script to setup up everything, that is needed. After successful execution of the script you might need to update your `PATH` to run `pipenv`. To be able to build the Java Applets you need to switch to Java 1.8. The framework was developed using:
```
$ java -version 
openjdk version "1.8.0_265"
OpenJDK Runtime Environment (build 1.8.0_265-8u265-b01-0ubuntu2~18.04-b01)
OpenJDK 64-Bit Server VM (build 25.265-b01, mixed mode)
```
The bootstrapping script also tries to instruct you, what to do. In order to invoke `javus` you need to have all the Python dependencies accessible in your environemnt. One option is to activate the Python virtual environment with `pipenv shell` (you should see a change in prompt):

```
$ pipenv shell
Launching subshell in virtual environment…
 . $HOME/.local/share/virtualenvs/javus-lU2hMrWC/bin/activate

(javus) $
```

Then you can run `javus` simply by typing:

```
(javus) $ javus
usage: javus [-h] [-v VERBOSE] {web,run,list,enable,disable,validate} ...
javus: error: the following arguments are required: sub_command
```

Or indirectly with:

```
(javus) $ python scripts/javus 
usage: javus [-h] [-v VERBOSE] {web,run,list,enable,disable,validate} ...
javus: error: the following arguments are required: sub_command
```


### Run `javus` within Docker

If you want to avoid cluttering your system with additional software you can use [Docker](https://www.docker.com/) (installation of Docker is not covered here). The Docker image is currently not available for download, however, you can easily build it yourself (it will take a few minutes, but only needs to be run once). If you are using [Invoke](https://www.pyinvoke.org/) you can run:
```
$ inv dock
```
If not, you can build the Docker image `javus-container` directly from the root of the project:
```
$ docker build --tag javus-container:latest .
```
Once the build finishes you'll have a new Docker image `javus-container`. The invocation of the container is not straigthforward, because we need to make sure, that our results persist across Docker container runs and we also need to pass through the devices (smartcard readers). For convenience there is a Bash script `bin/javus-docker-unix`, that you can use to start the container. It behaves like a wrapper around the `scripts/javus` (so, the usage of the command line flags is the same). Instead of running `javus run --riskit` you can run `./bin/javus-docker-unix run --riskit`. Invocation through Docker is fragile - for example from testing it turned out that internal reader on a notebook was not recognized inside the Docker image and only an external one (connected through USB) has worked. At this momemnt this is up to the user to figure out, what works.

The list of available attacks is kept in `javus/data/registry.ini`. This file simply lists the attacks (divided into sections by their origin) and sets them to `yes` or `no` whether they are enable od disabled. You can enable/disable an attack using the `enable` and `disable` sub-command (you can specify more at once). No real attacks/POCs are currently enabled by default to make user run real test intentionally.

### Example testing session

In general the testing session might look like this (using the native invocation; some output was omitted):

```bash
$ pipenv shell
Launching subshell in virtual environment…
 . $HOME.local/share/virtualenvs/javus-lU2hMrWC/bin/activate
(javus) $ javus list
List of registered attacks.
enabled:
    example_attack

disabled:
    arraycopy
    arrayops
    baload_bastore
    localvars
    nativemethod
    referencelocation
    staticfield_ref
    swap_x
(javus) $ javus disable example_attack
(javus) $ javus enable swap_x
(javus) $ javus list
List of registered attacks.
enabled:
    swap_x

disabled:
    arraycopy
    arrayops
    baload_bastore
    localvars
    nativemethod
    referencelocation
    staticfield_ref
    example_attack
    (javus) $  javus git:(master) ✗ javus --verbose 50 run --riskit
Running the pre-analysis..
 ...
    [ 1/ 3] install: pass
    [ 2/ 3] send: pass
    [ 3/ 3] uninstall pass
Running the analysis..
Executing attacks from SECURITY EXPLORATIONS
arraycopy: skip
arrayops: skip
baload_bastore: skip
localvars: skip
nativemethod: skip
referencelocation: skip
staticfield_ref: skip
swap_x (SDK: jc221)
    [ 1/ 5] install: pass
    [ 2/ 5] install: pass
    [ 3/ 5] send: fail
    [ 4/ 5] uninstall pass
    [ 5/ 5] uninstall pass
swap_x (SDK: jc222)
    [ 1/ 5] install: pass
    [ 2/ 5] install: pass
    [ 3/ 5] send: fail
    [ 4/ 5] uninstall pass
    [ 5/ 5] uninstall pass
...
Executing attacks from SERGEI VOLOKITIN
Executing attacks from JIP HOGENBOOM and WOJCIECH MOSTOWSKI
Executing attacks from EXAMPLE
example_attack: skip
Executing attacks from DEVELOPMENT
Running the post-analysis..
(javus) $ javus web
```

And go to your browser to `localhost:5000`. In case you are using the Docker container you need to change the website host to `0.0.0.0` for it to be accessible outside of the image. In other words, start the local website in Docker like this:
```
$ ./bin/javus-docker-unix web --host 0.0.0.0
```

Again, you are running this tool at your own risk.

Licensing
---------

The code related to the framework itself is MIT licensed. However, some of the POCs (namely, those from [Security Explorations](http://www.security-explorations.com/javacard_details.html)) have different license. Therefore using code from this repository should be done with care -- if in doubt, add an issue and ask the authors. More details are [here](https://github.com/quapka/javus/tree/master/javus/data/attacks).

Contribution
------------
TODO
