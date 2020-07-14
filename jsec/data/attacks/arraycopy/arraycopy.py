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
            "payload": "0x80 0x10 0x01 0x02	0x04	0x00 0x00 0xc0 0x00				0x7F",
            "comment": "READ MEM",
            "optional": True,
        },
        {
            "name": "send",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x0a 0x04 0x00 0xaa 0xbb 0xcc 0xdd		0x7F",
            "comment": "WRITE MEM",
            "optional": True,
        },
        {
            "name": "send",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x0e 0x04 0x01 0x11 0x22 0x33 0x44		0x7F",
            "comment": "WRITE MEM",
            "optional": True,
        },
        {
            "name": "send",
            "payload": "0x80 0x10 0x01 0x02	0x04	0x00 0x00 0xc0 0x01				0x7F",
            "comment": "READ MEM",
            "optional": True,
        },
    ]
