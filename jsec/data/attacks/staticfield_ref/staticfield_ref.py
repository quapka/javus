class Stages:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/com/se/vulns/javacard/vulns.new.cap",
            "comment": "The altered vulnerable applet",
            # install should be required by default
            "optional": False,
        },
        {
            # the name directly translates to the methods, that will be called
            "name": "install",
            # path relative to the directory of the attack
            "path": "build/{version}/com/se/applets/javacard/applets.cap",
            # comment/description of the stage
            "comment": "The base applet",
            # install should be required by default
            "optional": False,
        },
        {
            "name": "send",
            "comment": "GET_STATIC APDU",
            "payload": "0x80 0x10 0x01 0x02	0x01	0x00	0x7F",
        },
    ]
