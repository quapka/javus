#!/bin/bash
now="$(date +%H_%M-%d_%b_%G)"
./convert-scr.py ../script/test.scr | while read payload
do
    java -jar "/home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar" --verbose --debug --apdu "$payload" 2>&1 | tee -a logs/apdu."$now".log
done
