from autopycli import Arguments
from autopycli import Configuration
from autopycli import Environment


class CliRuntime:
    def __init__(self, *args, **kwargs):
        self.arguments = Arguments(args, kwargs)
