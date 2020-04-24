#/bin/bash
gp="java -jar /home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar"

# save output
$gp --verbose\
    --debug\
    --install build/$1/com/se/vulns/javacard/vulns.new.cap

# save output
$gp --verbose\
    --debug\
    --install build/$1/com/se/applets/javacard/applets.cap

$gp --verbose\
    --debug\
    --apdu 00a404000aA00000006503010C0101\
    --apdu 80100102040000C0007F\
    --dump stage.name
#     --apdu 8011010208000a0400aabbccdd7f\
#     --apdu 8011010208000e0401112233447f\
#     --apdu 80100102040000c0017f\

# save output
$gp --verbose\
    --debug\
    --uninstall build/$1/com/se/applets/javacard/applets.cap

# save output
$gp --verbose\
    --debug\
    --uninstall build/$1/com/se/vulns/javacard/vulns.new.cap
