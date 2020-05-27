import configparser
import os

from jsec.settings import get_project_root


# TODO give more reasonable output to the user in case of a failure
# https://docs.pytest.org/en/latest/assert.html
# FIXME pytest is now user not dev requirement
class CheckUserConfiguration(object):
    def setup_method(self, method):
        self.project_root = get_project_root()

    def check_presences_of_user_configuration(self):
        project_dir = os.listdir(self.project_root)
        assert "user-config.ini" in project_dir

    def check_user_config_is_valid(self):
        config = configparser.ConfigParser(strict=True)
        config_file = os.path.join(self.project_root, "user-config.ini")

        config.read(config_file)
        config.sections()


# TODO add check on user defined attacks etc., e.g. that they are importable
# through importlib
