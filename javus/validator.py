from javus.builder import get_builder
from javus.executor import get_executor
from javus.settings import ATTACKS, DATA
from javus.utils import AttackConfigParser
from javus.builder import get_builder
from javus.executor import get_executor
import configparser
import importlib

from pathlib import Path


class AttackValidator:
    def __init__(self):
        self.validators = [
            "validate_attackdir",
            "validate_name",
            "validate_required_files",
            "validate_is_registered",
            "validate_config_file",
            "validate_builder",
            "validate_executor",
        ]

    def validate_attackdir(self, attack):
        self.workdir = ATTACKS / attack
        valid = self.workdir.exists()
        if not valid:
            print("Error: the attack directory '%s' does not exists" % self.workdir)
        return valid

    def validate_name(self, attack):
        valid = str.isidentifier(attack)
        if not valid:
            print(
                "Error: the attack name '%s' is not a valid Python identifier" % attack
            )
        return valid

    def validate_required_files(self, attack):
        valid = True
        filepaths = [
            Path("config.ini"),
            Path("build.xml"),
            Path("%s.py" % attack),
            Path("aids.ini"),
        ]

        for path in filepaths:
            fullpath = self.workdir / path
            if not (self.workdir / path).exists():
                print(
                    "Error: the filepath '%s' is missing in the attack directory '%s'. Please, add it."
                    % (path, self.workdir)
                )
                valid = False

        return valid

    def validate_is_registered(self, attack):
        self.registry = configparser.ConfigParser()
        self.registry.read(DATA / "registry.ini")

        valid = False
        for section in self.registry.sections():
            for value in self.registry[section]:
                if value == "module":
                    continue
                if value == attack:
                    valid = True
                    enabled = (
                        "enabled"
                        if self.registry.getboolean(section, attack)
                        else "disabled"
                    )
                    break
            if valid:
                break

        if valid:
            print(
                "Note: the attack '%s' is registered under section '%s' and is '%s'."
                % (attack, section, enabled)
            )
            self.section = section
        return valid

    def get_module(self, attack):
        try:
            module = self.registry.get(self.section, "module")
            return module
        except KeyError:
            return ""

    def validate_config_file(self, attack):
        config = AttackConfigParser()
        filepath = self.workdir / "config.ini"
        config.read(filepath)
        valid = False
        try:
            config["BUILD"]["versions"]
            valid = True
        except KeyError:
            print(
                "Error: the 'versions' key is missing from the 'BUILD' section in '%s'"
                % filepath
            )
            valid = False

        if valid:
            try:
                config.get_sdk_versions("BUILD", "versions")
            except:
                print(
                    "Error: the 'versions' key cannot be loaded properly. "
                    "Is it a comma separated list of SDK versions?"
                )
                valid = False

        return valid

    def validate_builder(self, attack):
        module = self.get_module(attack)
        builder = get_builder(attack_name=attack, module=module)
        print("Note: the attack is using the '%s' as its AttackBuilder." % builder)
        return True

    def validate_executor(self, attack):
        module = self.get_module(attack)
        executor = get_executor(attack_name=attack, module=module)
        print("Note: the attack is using the '%s' as its AttackExecutor." % executor)
        return False

    def validate_scenario(self, attack):
        modulefile = self.workdir / "%s.py" % attack
        # FIXME validate the stages

    def validate_attack(self, attack):
        valid = True

        for name in self.validators:
            try:
                validator = getattr(self, name)
            except AttributeError:
                continue

            valid = validator(attack)
            if not valid:
                break

        return valid

    def run(self, attacks: list):
        for attack in attacks:
            valid = self.validate_attack(attack)
            if valid:
                print("The attack '%s' is configured correctly." % attack)
            else:
                print("The attack '%s' is not configured correctly." % attack)


if __name__ == "__main__":
    validator = AttackValidator()
    validator.run(["example_attack"])
