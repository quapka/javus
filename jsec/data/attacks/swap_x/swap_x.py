class Scenario:
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
            "comment": "TRIGGER_SWAPX",
            "payload": "0x80 0x10 0x01 0x02	0x01	0x00	0x7F",
        },
    ]
