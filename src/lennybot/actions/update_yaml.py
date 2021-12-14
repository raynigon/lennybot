from ..config.config import LennyBotActionConfig
from .iaction import IAction
from types import SimpleNamespace
from yamlpath.common import Parsers
from yamlpath.wrappers import ConsolePrinter
from yamlpath import Processor

class UpdateYamlAction(IAction):

    def __init__(self, name, target_version, config: LennyBotActionConfig) -> None:
        self._name = name
        self._target_version = target_version
        self._target_file = config.target_file
        self._yaml_path = config.yaml_path
        if config.value_pattern is not None:
            self._value_pattern = config.value_pattern
        else:
            self._value_pattern = "{{version}}"

    @property
    def application(self) -> str:
        return self._name

    @property
    def target_version(self) -> str:
        return self._target_version

    def run(self):
        logging_args = SimpleNamespace(quiet=True, verbose=False, debug=False)
        log = ConsolePrinter(logging_args)
        yaml = Parsers.get_yaml_editor()
        (yaml_data, doc_loaded) = Parsers.get_yaml_data(yaml, log, self._target_file)
        if not doc_loaded:
            raise Exception("Yaml document could not be loaded")
        processor = Processor(log, yaml_data)
        processor.set_value(self._yaml_path, self._create_value())
        with open(self._target_file, "w") as file_ptr:
            yaml.dump(yaml_data, stream=file_ptr)

    def _create_value(self):
        return self._value_pattern.replace("{{version}}", self._target_version)
