from CLI.main import CLI
from API.main import API

def main():
    Api = API()
    Api.load_cache()
    defaults = Api.get_param_suggestions()

    Cli = CLI(defaults)
    params = Cli.run()
    Api.run(params)

if __name__ == '__main__':
    main()
