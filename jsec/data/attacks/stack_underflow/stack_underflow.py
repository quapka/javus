# FIXME need to figure generation of bytecode
class Stages:
    STAGES = [
        {"name": "install", "path": "build/{version}/cast_to_short-{version}.cap",},
        {
            "name": "send",
            "comment": "READMEM APDU",
            "payload": "0xA0 0xB0 0x01 0x00	0x00",
            "optional": False,
        },
    ]
