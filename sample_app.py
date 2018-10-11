import os
import pprint
from autopycli import CliRuntime
from autopycli import logger

PP = pprint.PrettyPrinter()


def main():
    runtime = CliRuntime(description="Some CLI app", config_path=os.path.join(os.getcwd(), "config_dir"))
    runtime.add_argument(dest="required", help="A required positional")
    runtime.add_argument("positional", nargs="+", help="A list of required positional arguments")
    runtime.add_argument("--malformed", "--supermalformed", help="A malformed argument", required=True)
    runtime.add_argument("-s", "--sample_var", required=True, help="A required argument")
    runtime.add_argument("-o", "--optional_var", dest="optional_var", help="An optional argument")
    runtime.add_argument("-c", "--config_var", dest="config_var", required=True, help="A configurable option")
    runtime.add_argument("-e", "--env_var", dest="env_var", help="An environment variable")
    runtime.add_argument("-d", "--default_var", dest="default_var", default="somedefault",
                         help="An argument with a default")
    runtime.parse_args()
    PP.pprint(vars(runtime))
    PP.pprint(vars(runtime.arg_parser))
    logger.debug("Runtime config: {}".format(runtime.config))
    logger.debug("Required args: {}".format(runtime.required_args))
    logger.debug("Error messages: {}".format(runtime.error_messages))


if __name__ == "__main__":
    main()
