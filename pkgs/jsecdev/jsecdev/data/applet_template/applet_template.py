from jsec.executor import BaseAttackExecutor


class Stages:
    STAGES = [
        {
            # 'install' is one of the predefined stages
            "name": "install",
            # {version} is dynamically populated with the SDK version
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
            # 'payload' is the payload, that will be send to
            "payload": "80 01 00 00 02",
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
        # implicitly there is also 'uninstall' stage(s), which will attempt to
        # uninstall all successfully installed applets
    ]


class AttackExecutor(BaseAttackExecutor):
    def _pre_custom_stage(self, *args, **kwargs):
        """
        The `_pre_<stage-name>` is the place, where you can perform some additional setup
        in case you need to do so. The difference from the other stage methods is, that in
        case it returns something it is not saved anywhere.
        """
        pass

    def _custom_stage(self, param1, *args, **kwargs):
        """
        This is the main stage method. For example for `send` stage this is the place, where
        the `payload` is sent to the JavaCard.
        """
        pass

    def _assess_custom_stage(self, result, *args, **kwargs):
        """
        This is the method, that can interpret the results of the stage. It's main goal
        is to set the `result['success']` to either `True` or `False`.
        """
        pass
