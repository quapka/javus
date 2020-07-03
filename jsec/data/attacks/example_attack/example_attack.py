from jsec.executor import BaseAttackExecutor


class Stages:
    STAGES = [
        {
            # 'install' is one of the predefined stages
            "name": "install",
            # {version} is dynamically populated with the SDK version, e.g. jc222
            "path": "build/{version}/example-attack-{version}.cap",
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
            "name": "custom_stage",
            "param1": "value",
            "comment": "My new stage",
            "optional": False,
        }
        # implicitly there is also 'uninstall' stage(s), which will attempt to
        # uninstall all successfully installed applets
    ]


class AttackExecutor(BaseAttackExecutor):
    def _prepare_custom_stage(self, *args, **kwargs):
        """
        The `_prepare_<stage-name>` is the place, where you can perform some additional setup
        in case you need to do so. The difference from the other stage methods is, that in
        case it returns something it is not saved anywhere.
        """
        pass

    def _custom_stage(self, param1, *args, **kwargs):
        """
        This is the main stage method. For example for `send` stage this is the place, where
        the `payload` is sent to the JavaCard.
        """
        result = {}
        return result

    def _assess_custom_stage(self, result, *args, **kwargs):
        """
        This is the method, that can interpret the results of the stage. It's main goal
        is to set the `result['success']` to either `True` or `False`.
        """
        result["success"] = True
        return result
