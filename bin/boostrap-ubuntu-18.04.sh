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
    swig\
    libpcsclite-dev\
    git \
    python3 \
    python3-pip\
    openjdk-8-jdk-headless\
    maven\
    pcscd\
    mongodb\
    ant\
    ant-contrib
    

echo "installing pipenv.."
if pip3 install --user pipenv; then
    if ! which pipenv; then
        echo "Pipenv was installed, but is not in your PATH"
        echo "You can try to find it by running:"
        echo "$ find / -iname pipenv 2>/dev/null"
        echo "Once it is in your PATH run this bootstrap script again"
        PIPENV_TO_PATH=true
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
~/.local/bin/pipenv install --dev
# update oracle_javacard_sdks
git submodule update --init --recursive --jobs 8

echo "updating Java alternative to 1.8.0"
java_8_jdk="$(update-java-alternatives -l | grep 1.8.0 | awk '{ print $3 }')"
if [[ java_8_jdk == "" ]]; then
    echo "Error: cannot find java-1.8.0-openjdk. Please, try to install it manually."
    NEED_INSTALL_JAVA_8_JDK=true
else
    sudo update-java-alternatives --set "$java_8_jdk"
fi

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

echo "The installations and setup to bootstrap your environment is done."
echo "See below for any errors, that need to be resolved."

if [ "$PIPENV_TO_PATH" = true ]; then
    echo "In order to use 'pipenv' in the future you'll need to add it to your PATH"
    echo "environment variable. It should be located in $HOME/.local/bin."
    echo "If so, add the following line to your .bashrc or .profile, whichever you"
    echo "prefere."
    echo "export PATH=\"\$PATH:$HOME/.local/bin\""
fi

if [ "$NEED_INSTALL_JAVA_8_JDK" = true ]; then
    echo "In order to run the application a Java 1.8.0 is needed."
    echo "You can try to install it manually by running:"
    echo "$ apt install openjdk-8-jdk-headless"
    echo "Once it is installed you also need to set it up as your current Java alternative"
    echo "To do so run and follow the instructions of:"
    echo "$ update-alternatives --config java"
    echo" Afterwards validate, that it is setup correctly by running:"
    echo "$ java -version"
fi
