import argparse
from . import dynamodbfaker

def main():
    parser = argparse.ArgumentParser(description=get_description())
    parser.add_argument('--config', required=True, help='Config yaml file path')
    parser.add_argument('--target', required=False, help='Target folder/file')
    parser.add_argument('--to', required=False, help='Write to dynamodb/file')

    args = parser.parse_args()

    config_file_path = None
    target_file_path = None
    target_system = None

    if args.config is not None:
        config_file_path = args.config
    else:
        print("Missing --config parameter. Use --help for more detail.")
        return

    if args.target is not None:
        target_file_path = args.target
    else:
        target_file_path = "."  

    if args.to is not None:
        target_system = args.to
    else:
        target_system = "file"


    if isinstance(config_file_path, str) and target_system == "file":
        dynamodbfaker.to_target("json", config_file_path, target_file_path)
    elif isinstance(config_file_path, str) and target_system == "dynamodb":
        dynamodbfaker.to_dynamodb(config_file_path, target_file_path)
    else:
        print("Wrong paramater(s)")
        print(get_description())

def get_description():
    return "more detail: https://github.com/necatiarslan/dynamodb-faker/blob/main/README.md"

if __name__ == '__main__':
    main()



