#!/bin/bash

if grep docker /proc/1/cgroup --quiet; then
    echo "Running inside docker"
    # TODO move to ./boostratp-live-container ?
    echo "Starting pcscd deamon"
    service pcscd start
    echo "Checking pcscd daemon status:"
    service pcscd status

    echo "Starting MongoDB"
    service mongodb start
    echo "Checking MongoDB daemon status:"
    service mongodb status

else
    echo "Running outside of docker"
fi

if [ "$1" == "--DEBUG-DOCKER" ];
then
    echo "In a poor man's debug mode"
    python3
else
    pipenv run python scripts/javus $@
fi
