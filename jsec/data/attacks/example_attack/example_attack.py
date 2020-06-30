class Stages:
    STAGES = [
        {
            # 'install' is one of the predefined stages
            "name": "install",
            # {version} is dynamically populated with the SDK version, e.g. jc222
            "path": "build/{version}/javacardversion-{version}.cap",
            # 'optional' determines, whether we want to continue performing
            # the following stages is this stage fails
            "optional": False,
            # TODO add a tag to have something for 'send' stages to specify
            # where to send the payload
        },
        {
            # 'send' is another already predefined stage
            "name": "send",
            # 'payload' is the payload, that will be send to, there are multiple ways of
            # defining a payload
            "payload": "80 01 00 00 02",
            # to improve readability the comment can span multiple lines, just make sure
            # that it is done in such a way, that the value is still a string
            "comment": (
                "This comment will be saved along the results of this stage."
                "Description of this stage can be added here."
                "This payload represents success"
            ),
            "optional": True,
        },
        {
            # 'send' is another already predefined stage
            "name": "send",
            "payload": "80 02 00 00 02",
            "comment": "This payload represents failure",
            "optional": True,
        },
        {
            "name": "custom",
            "comment": "My new stage"
            "optional": False,
        # implicitly there is also 'uninstall' stage(s), which will attempt to
        # uninstall all successfully installed applets
    ]
