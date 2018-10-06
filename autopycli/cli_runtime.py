import inspect
import os

import autopycli.arguments as cliargs
from autopycli import ArgumentsError
from autopycli import Configuration
from autopycli import Environment

ARG_PARSER = cliargs.ArgumentParser


class RuntimeConfig:
    def __repr__(self):
        return "RuntimeConfig({})".format(str(self.__dict__))

    def __str__(self):
        members = ["{}: {}".format(k, str(self.__dict__[k])) for k in self.__dict__]
        return "{{{}}}".format(", ".join(members))


class CliRuntime:
    def __init__(self, *args, **kwargs):
        self.runtime_config = RuntimeConfig()
        self.required_args = []
        self.error_messages = []
        self.config_path = kwargs.get("config_path")
        self.env_vars = os.environ
        parser_kwargs = self.filter_parser_args(ARG_PARSER, kwargs)
        self.arg_parser = ARG_PARSER(*args, **parser_kwargs)

    def filter_parser_args(self, parser, kwargs):
        """Return keyword args that are valid for the given parser.

        Exclude comparisons with the 0th element in the argspec, as it
        is the instance variable (i.e., "self").
        """
        arg_spec = inspect.getargspec(parser.__init__)
        return {k: kwargs[k] for k in kwargs if k in arg_spec.args[1:]}

    def add_argument(self, *args, **kwargs):
        if kwargs.get("required"):
            # TODO: Decide which is more correct
            #self.required_args.append(kwargs["dest"])
            self.required_args.append(kwargs.get("dest"))

        self.arg_parser.add_argument(*args, **kwargs)

    def load_configs(self):
        return

    def parse_args(self):
        try:
            self.arg_parser.parse_args(namespace=self.runtime_config)
        except ArgumentsError as exc:
            self.error_messages.append(str(exc))

        self.load_configs()
