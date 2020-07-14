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
            "comment": "NREAD_SHORT",
            "payload": "0x80 0x10 0x01 0x02	0x06	0x00 0x00 0x00 0x00 0x00 0x00			0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "NWRITE_SHORT",
            "payload": "0x80 0x11 0x01 0x02	0x08	0x00 0x00 0x00 0x00 0x00 0x00 0x11 0x22		0x7F",
            "optional": False,
        },
    ]
