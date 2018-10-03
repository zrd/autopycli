import argparse


class Arguments:
    def __init__(self, *args, **kwargs):
        self.arg_parser = argparse.ArgumentParser(args, kwargs)

    def add_argument(self, *args, **kwargs):
        self.arg_parser.add_argument(args, kwargs)

    def parse_args(self):
        return self.arg_parser.parse_args()
