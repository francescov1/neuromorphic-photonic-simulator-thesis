from CLI.main import CLI
from API.main import API


from pprint import pprint


def main():
    Api = API()
    defaults = Api.get_param_suggestions()

    Cli = CLI(defaults)
    params = Cli.run()

    #pprint(params)
    Api.run(params)


if __name__ == '__main__':
    main()
