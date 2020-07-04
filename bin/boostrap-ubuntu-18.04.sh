#!/bin/bash

if [[ "$0" != "./boostrap-ubuntu-18.04.sh" ]]; then
    echo "Please, run this script directly from the jcvm-analysis/bin/ directory."
    echo "That is, change directory into it and execute:"
    echo "$ ./boostrap-ubuntu-18.04.sh"
    exit 1
fi

echo "This bootstrap script was tested on Ubuntu 18.04"
echo
echo "This script will attempt to install all requirements for the jsec"
echo "utility to work. Before running this script you should read through it"
echo "carefully to see, what it does. This script needs root privileges"
echo "at some places."
echo

read -p "Do you want to continue with the boostrapping? [Y/n]" -n 1 -r
echo    # (optional) move to a new line
if ! [[ $REPLY =~ ^[Yy]$ ]];
then
    echo "Exiting. Nothing has been installed."
    exit 0
fi


echo "updating the repositories.."
sudo apt update
echo "installing the software dependencies.."
sudo apt install --yes\
    git \
    python3 \
    python3-pip\
    openjdk-8-jdk-headless\
    maven\
    pcscd\
    mongodb\
    

echo "installing pipenv.."
if pip3 install --user pipenv; then
    if ! which pipenv; then
        echo "Pipenv was installed, but is not in your PATH"
        echo "You can try to find it by running:"
        echo "$ find / -iname pipenv 2>/dev/null"
        echo "Once it is in your PATH run this bootstrap script again"
    fi
else
    echo "Error: pipenv could not be installed."
    echo "Try running manually:"
    echo "$ pip3 install --user pipenv"
    echo "Resolve any issues and run this bootstrap script again."
    exit 1
fi

# go to the root directory of the project
pushd ../

# # GlobalPlatformPro
# git clone https://github.com/MartinPaljak/GlobalPlatformPro.git
# pushd GlobalPlatformPro
# popd

# git clone https://github.com/MartinPaljak/ant-javacard
# pushd ant-javacard
# ./mvnw package
# popd

echo "installing the Python dependencies.."
# go to the project root directory and install all Pipenv dependencies
pipenv install --dev
# update oracle_javacard_sdks
git submodule update --init --recursive --jobs 8

# prepare GlobalPlatformPro
pushd submodules/GlobalPlatformPro
echo "checking out old GlobalPlatformPro commit"
git checkout 2d4bb36c145bd8c13606f12aa14e6e29d8ecef78
echo "building gp.jar.."
mvn package
popd

# prepare ant-javacard
pushd submodules/ant-javacard
echo "building ant-javacard.jar.."
./mvnw package
popd

# export JCVM_ANALYSIS_HOME="$(pwd)"
# export FLASK_APP="$(pwd)/jsec/viewer.py"
popd

# swig3.0 \
# swig \
# python3-swiglpk \
# libpcsclite-dev \
# # smartcard deamon
# pcscd \
# # install pkcs11-tool - only for development
# opensc \
# ant \
# ant-contrib \
# software-properties-common \
# python3-pip \
# git \
# openjdk-8-jdk \
# maven \
# mongodb
