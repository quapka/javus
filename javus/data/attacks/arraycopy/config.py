# stages
# install requires path and optionally version?
# uninstall requires what to uninstall
# send requires AID for applet selection and raw bytes to be sent
# but applet AID might be altered in case it is already installed
# // Select SEApplet //aid/A000000062/03010C0101
STAGES = [
    {"install": "build/{version}/com/se/applets/javacard/applets.cap"},
    {"install": "build/{version}/com/se/vulns/javacard/vulns.new.cap"},
    {
        "send": [0x80, 0x10, 0x01, 0x02, 0x04, 0x00, 0x00, 0xC0, 0x00, 0x7F],
        "comment": "READMEM APDU",
    },
    {
        "send": [
            0x80,
            0x11,
            0x01,
            0x02,
            0x08,
            0x00,
            0x0A,
            0x04,
            0x00,
            0xAA,
            0xBB,
            0xCC,
            0xDD,
            0x7F,
        ],
        "comment": "WRITEMEM APDU",
    },
    {
        "send": [
            0x80,
            0x11,
            0x01,
            0x02,
            0x08,
            0x00,
            0x0E,
            0x04,
            0x01,
            0x11,
            0x22,
            0x33,
            0x44,
            0x7F,
        ],
        "comment": "WRITEMEM APDU",
    },
    {
        "send": [0x80, 0x10, 0x01, 0x02, 0x04, 0x00, 0x00, 0xC0, 0x01, 0x7F],
        "comment": "READMEM APDU",
    },
    # {"uninstall": "yes"},
]
