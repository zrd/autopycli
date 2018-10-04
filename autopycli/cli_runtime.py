import autopycli.arguments as cliargs
from autopycli import ArgumentsError
from autopycli import Configuration
from autopycli import Environment


class RuntimeConfig:
    def __repr__(self):
        return "RuntimeConfig({})".format(str(self.__dict__))

    def __str__(self):
        members = ["{}: {}".format(k, str(self.__dict__[k])) for k in self.__dict__]
        return "{{{}}}".format(", ".join(members))


class CliRuntime:
    def __init__(self, *args, **kwargs):
        self.arg_parser = cliargs.ArgumentParser(*args, **kwargs)
        self.runtime_config = RuntimeConfig()
        self.required_args = []
        self.error_messages = []

    def add_argument(self, *args, **kwargs):
        if kwargs.get("required"):
            self.required_args.append(kwargs["dest"])

        self.arg_parser.add_argument(*args, **kwargs)

    def parse_args(self):
        try:
            self.arg_parser.parse_args(namespace=self.runtime_config)
        except ArgumentsError as exc:
            self.error_messages.append(str(exc))
