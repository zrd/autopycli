import os
import pprint
from autopycli import CliRuntime
from autopycli import logger

PP = pprint.PrettyPrinter()


def main():
    runtime = CliRuntime(description="Some CLI app", config_path=os.path.join(os.getcwd(), "resources", "app_config"))
    runtime.add_argument(dest="required", help="A required positional")
    runtime.add_argument("positional", nargs="+", help="A list of required positional arguments")
    runtime.add_argument("--malformed", "--supermalformed", help="A malformed argument", required=True)
    runtime.add_argument("-o", "--optional", dest="optional_var", help="An optional argument")
    runtime.add_argument("-c", "--config", dest="config_var", required=True, help="A configurable option")
    runtime.add_argument("-v", "--override", required=True, help="An option to override")
    runtime.add_argument("-e", "--env", dest="env_var", help="An environment variable")
    runtime.add_argument("-d", "--default_var", dest="default_var", default="somedefault",
                         help="An argument with a default")
    runtime.add_argument("-u", "--user_configs", nargs="+", dest="some_bizarre_name",
                         config=True, help="One or more paths to user-specified config files or dirs")
    runtime.parse_args()
    #PP.pprint(vars(runtime))
    logger.debug("Runtime config: {}".format(runtime.config))
    logger.debug("Required args: {}".format(runtime.required_args))
    logger.debug("Errors: {}".format(runtime.errors))


if __name__ == "__main__":
    main()
