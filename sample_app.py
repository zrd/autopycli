import os

from autopycli import CliRuntime

CONFIG_PATH = os.path.join(os.getcwd(), "sample.conf")


def main():
    app_config = CliRuntime(description="Some CLI app")
    app_config.arguments.add_argument("-s", "--sample", dest="sample_var", required=True, help="A required argument")
    app_config.arguments.add_argument("-o", "--option", dest="optional_var", help="An optional argument")


if __name__ == "__main__":
    main()
