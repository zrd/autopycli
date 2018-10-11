import configparser
import inspect
import os

import autopycli.arguments as cliargs
from autopycli import ArgumentsError
from autopycli import Configuration
from autopycli import Environment

ARG_PARSER = cliargs.ArgumentParser


class RuntimeConfig:
    """Carry the application's config.

    RuntimeConfig should only be a member of a CliRuntime instance. No
    special constructor behavior is needed here.
    """
    def __repr__(self):
        return "RuntimeConfig({})".format(str(self.__dict__))

    def __str__(self):
        members = ["{}: {}".format(k, str(self.__dict__[k])) for k in self.__dict__]
        return "{{{}}}".format(", ".join(members))


class CliRuntime:
    """Load available config channels into a RuntimeConfig.

    A "config channel" is any viable route to bind a configuration
    value to a key name, such as command line arguments, config file
    options, and environment variables. As of now these include the
    most obvious standard library packages argparse, configparser, and
    os. In the future they could include Click based interfaces; YAML,
    XML, or JSON config files; etc.

    Order of precedence should be::
        Command Line > Config File(s) > Environment
    """
    def __init__(self, *args, **kwargs):
        self.config = RuntimeConfig()
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

    def load_config_file(self, filepath):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        for section in parser:
            self.config.__dict__.update({k: parser[section][k]
                                         for k in parser[section]
                                         if not self.config.__dict__.get(k)})

    def load_configs(self, config_extns=(".ini", ".cfg", ".conf", ".config")):
        """Load config file(s)

        If config_path is a directory, load all config files in the
        directory in some (unknowable) order. If a file, load the file
        if it's a recognizable config file.
        """
        if self.config_path:
            if os.path.isdir(self.config_path):
                for dirpath, _, filenames in os.walk(self.config_path):
                    for file_path in [os.path.join(dirpath, f) for f in filenames if f.endswith(config_extns)]:
                        self.load_config_file(file_path)
            elif os.path.isfile(self.config_path) and self.config_path.endswith(config_extns):
                self.load_config_file(self.config_path)

    def parse_args(self):
        try:
            self.arg_parser.parse_args(namespace=self.config)
        except ArgumentsError as exc:
            self.error_messages.append((self.arg_parser.__class__, str(exc)))

        self.load_configs()
