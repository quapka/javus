class Stages:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/com/se/vulns/javacard/vulns.new.cap",
            "comment": "",
        },
        {
            "name": "install",
            "path": "build/{version}/com/se/applets/javacard/applets.cap",
        },
        {
            "name": "send",
            "comment": "PING APDU",
            "payload": "0x80 0x10 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "STATUS APDU",
            "payload": "0x80 0x11 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "SETUP APDU",
            "payload": "0x80 0x12 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "READMEM APDU",
            "payload": "0x80 0x13 0x01 0x02	0x03	0x00 0x00 0xc0		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "CLEANUP APDU",
            "payload": "0x80 0x15 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": False,
        },
        {
            "name": "uninstall",
            "path": "build/{version}/com/se/vulns/javacard/vulns.new.cap",
        },
        {
            "name": "uninstall",
            "path": "build/{version}/com/se/applets/javacard/applets.cap",
        },
    ]
