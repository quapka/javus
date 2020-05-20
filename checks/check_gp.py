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

    @pytest.mark.skip("Takes too long")
    def check_for_specific_gp_version(self):
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)
        gp.process_config()

        gp.read_gp_version()
        assert gp.version == "GlobalPlatformPro v20.01.23-0-g5ad373b"

    def check_that_gp_is_working(self):
        gp = GlobalPlatformProWrapper(config=self.config, dry_run=False)
        gp.process_config()

        gp.verify_gp()
        assert gp.works == True
