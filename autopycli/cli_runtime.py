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
        """Preprocess arguments passed to the arg parser.

        First, determine which of the provided args and kwargs are
        required. If not found in the commandline arguments, they will
        be expected from config files or environment variables.

        Then, call the arg parser's add_argument() method with the
        provided arguments.
        """
        if len(args) > 0:
            # A name or flags are provided.
            if not args[0].startswith("-"):
                # Name: bare positional.
                try:
                    self.required_args.append(kwargs["dest"])
                except KeyError:
                    self.required_args.append(args[0])
            elif kwargs.get("required") is True:
                # Flag(s): Normally optional, but have a "required" parameter.
                initial_num_required = len(self.required_args)
                try:
                    self.required_args.append(kwargs["dest"])
                except KeyError:
                    for arg in args:
                        if arg.startswith("--"):
                            # Long argument name. Ignore any long names after the first.
                            self.required_args.append(arg.lstrip("--"))
                            break

                if len(self.required_args) == initial_num_required:
                    # Short argument name.
                    self.required_args.append(args[0].lstrip("-"))
        elif kwargs.get("dest"):
            # No name or flags are provided, but "dest" is.
            self.required_args.append(kwargs["dest"])

        self.arg_parser.add_argument(*args, **kwargs)

    def load_configs(self):
        return

    def parse_args(self):
        try:
            self.arg_parser.parse_args(namespace=self.runtime_config)
        except ArgumentsError as exc:
            self.error_messages.append(str(exc))

        self.load_configs()
