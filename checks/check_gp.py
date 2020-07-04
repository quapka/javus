import configparser

import pytest

from jsec.gppw import GlobalPlatformProWrapper


# FIXME should be reimplemented as pytest check rather
@pytest.mark.live
class CheckGlobalPlatformPro:
    def setup_method(self, method):
        self.config = configparser.ConfigParser()
        # FIXME the path needs to be loaded dynamically
        self.config["PATHS"] = {
            "gp.jar": "/home/qup/projects/fi/crocs/GlobalPlatformPro/gp.jar",
        }

    def check_for_specific_gp_version(self):
        """
        Unfortunately, we need to use a specific commit, before the `--dump`
        command line option has been removed.
        """
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)
        gp.process_config()

        gp.read_gp_version()
        expected_version = "GlobalPlatformPro v20.01.23-6-g2d4bb36"
        assert gp.version == expected_version, (
            "The GlobalPlatformPro version currently needs to be fixed to the commit "
            "with hash %s. Make sure, that you are using this version."
            % expected_version
        )

    def check_that_gp_is_working(self):
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)

        gp.verify_gp()
        assert gp.works == True
