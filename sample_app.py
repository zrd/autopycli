import os
import pprint
from autopycli import CliRuntime
from autopycli import logger

CONFIG_PATH = os.path.join(os.getcwd(), "sample.conf")
PP = pprint.PrettyPrinter()


def main():
    app_config = CliRuntime(description="Some CLI app", config_path="/some/path/to/config")
    app_config.add_argument(dest="required", help="A required positional")
    app_config.add_argument("positional", nargs="+", help="A list of required positional arguments")
    app_config.add_argument("--malformed", "--supermalformed", help="A malformed argument", required=True)
    app_config.add_argument("-s", "--sample_var", required=True, help="A required argument")
    app_config.add_argument("-o", "--optional_var", dest="optional_var", help="An optional argument")
    app_config.add_argument("-c", "--config_var", dest="config_var", required=True, help="A configurable option")
    app_config.add_argument("-e", "--env_var", dest="env_var", help="An environment variable")
    app_config.add_argument("-d", "--default_var", dest="default_var", default="somedefault",
                            help="An argument with a default")
    app_config.parse_args()
    PP.pprint(vars(app_config))
    PP.pprint(vars(app_config.arg_parser))
    logger.debug("Runtime config: {}".format(app_config.runtime_config))
    logger.debug("Required args: {}".format(app_config.required_args))
    logger.debug("Error messages: {}".format(app_config.error_messages))


if __name__ == "__main__":
    main()
