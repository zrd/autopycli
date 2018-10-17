import configparser
import inspect
import os

import autopycli.arguments as cliargs
from autopycli import ArgumentsError
from autopycli import Configuration
from autopycli import Environment

ARG_PARSER = cliargs.ArgumentParser


class ArgparserNamespace:
    pass


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

    def add_option(self, section, kvpair):
        """Add a key-value pair to the specified config section.

        The name of the section is analogous to the section of an
        ini-style config file. In the current implementation, each
        unique section in the config file(s) will constitute a
        RuntimeConfig section, as will the command line arguments
        ("args") and the OS environment ("environ").

        `kvpair` must be a valid argument to the section dictionary's
        `update` method.
        """
        try:
            self.__dict__[section].update(kvpair)
        except KeyError:
            self.__dict__[section] = {}
            self.__dict__[section].update(kvpair)


class CliRuntime:
    """Load available config channels into a RuntimeConfig.

    A "config channel" is any viable route to bind a configuration
    value to a key name, such as command line arguments, config file
    options, and environment variables. As of now these include the
    obvious standard library packages argparse, configparser, and os.
    In the future they could include Click based interfaces; YAML, XML,
    or JSON config files; etc.

    Order of precedence should be::
        Command Line > Config File(s) > Environment
    """
    def __init__(self, *args, **kwargs):
        self.config = RuntimeConfig()
        self.config.add_option("environ", os.environ)
        self.required_args = []
        self.errors = []
        self.config_args = None
        self.config_path = self.get_config_path(kwargs)
        self.config_extns = kwargs.get("config_extns") or (".ini", ".cfg", ".conf", ".config")
        parser_kwargs = self.filter_parser_args(ARG_PARSER, kwargs)
        self._arg_parser = ARG_PARSER(*args, **parser_kwargs)

    def get_config_path(self, kwargs):
        config_path = kwargs.get("config_path")
        if isinstance(config_path, (bytes, str)):
            config_path = [config_path]
        elif config_path is None:
            config_path = []

        return config_path

    def filter_parser_args(self, parser, kwargs):
        """Return keyword args that are valid for the given parser.

        Exclude comparisons with the 0th element in the argspec, as it
        is the instance variable (i.e., "self").
        """
        arg_spec = inspect.getargspec(parser.__init__)
        return {k: kwargs[k] for k in kwargs if k in arg_spec.args[1:]}

    def add_argument(self, *args, **kwargs):
        """Preprocess an argument to be added to the arg parser.

        First, determine which of the provided args and kwargs are
        required. If not found in the commandline arguments, they will
        be expected from config files or environment variables.

        Then, check if the kwarg "config" is True. If so, the value of
        this argument signifies one or more paths to config files or
        directories.

        Finally, call the arg parser's add_argument() method with the
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
                            # Long argument name.
                            self.required_args.append(arg.lstrip("--"))
                            # Ignore any long names after the first.
                            break

                if len(self.required_args) == initial_num_required:
                    # Short argument name.
                    self.required_args.append(args[0].lstrip("-"))
        elif kwargs.get("dest"):
            # No name or flags are provided, but "dest" is.
            self.required_args.append(kwargs["dest"])

        # The value of this argument is one or more paths to config files or dirs.
        if kwargs.get("config") is True:
            self.config_args = kwargs.get("dest") or args
            # Don't pass it to the arg parser's add_argument method.
            del kwargs["config"]

        self._arg_parser.add_argument(*args, **kwargs)

    def load_config_file(self, filepath):
        parser = configparser.ConfigParser()
        parser.read(filepath)
        for section in parser:
            self.config.add_option(section, parser[section])

    def load_config_path(self, path):
        if os.path.isdir(path):
            for dirpath, _, filenames in os.walk(path):
                for file_path in [os.path.join(dirpath, f) for f in filenames if
                                  f.endswith(self.config_extns)]:
                    self.load_config_file(file_path)
        elif os.path.isfile(path):
            self.load_config_file(path)

    def load_configs(self):
        """Load config file(s).

        config_path can be a single path to a directory or a file, or a
        sequence of directories and/or files. For directory arguments,
        all files with a recognized extension will be loaded. The order
        in which they're loaded should be considered unknowable.
        """
        if self.config_args in self.config.__dict__:
            if isinstance(self.config.__dict__[self.config_args], (bytes, str)):
                self.config_path.append(self.config.__dict__[self.config_args])
            else:
                for arg in self.config_args:
                    if arg in self.config.__dict__:
                        self.config_path.append(self.config.__dict__[self.config_args])

        for path in self.config_path:
            self.load_config_path(path)

    def parse_args(self):
        ns = ArgparserNamespace()
        try:
            self._arg_parser.parse_args(namespace=ns)
        except ArgumentsError as exc:
            self.errors.append(exc)

        self.config.add_option("args", ns.__dict__)
        self.load_configs()
