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
            "comment": "READ MEM",
            "payload": "0x80 0x10 0x01 0x02	0x04	0x00 0x00 0xc0 0x00				0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "WRITE MEM",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x0a 0x04 0x00 0xaa 0xbb 0xcc 0xdd		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "WRITE MEM",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x0e 0x04 0x01 0x11 0x22 0x33 0x44		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "WRITE MEM",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x12 0x04 0x02 0x55 0x66 0x77 0x88		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "WRITE MEM",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x16 0x04 0x03 0x11 0x22 0x33 0x44		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "READ MEM",
            "payload": "0x80 0x10 0x01 0x02	0x04	0x00 0x00 0xc0 0x01				0x7F",
            "optional": False,
        },
    ]
