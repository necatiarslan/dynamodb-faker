import argparse
from . import dynamodbfaker

def main():
    parser = argparse.ArgumentParser(description=get_description())
    parser.add_argument('--config', required=True, help='Config yaml file path')
    parser.add_argument('--file_type', required=False, help='Target file type (csv,json,parquet,excel)')
    parser.add_argument('--target', required=False, help='Target folder/file')

    args = parser.parse_args()

    file_type = None
    config_file_path = None
    target_file_path = None

    if args.config is not None:
        config_file_path = args.config
    else:
        print("Missing --config parameter. Use --help for more detail.")
        return

    if args.file_type is not None:
        file_type = args.file_type
    else:
        file_type = "csv"

    if args.target is not None:
        target_file_path = args.target
    else:
        target_file_path = "."  


    if isinstance(config_file_path, str):
        dynamodbfaker.to_target(file_type, config_file_path, target_file_path)
    else:
        print("Wrong paramater(s)")
        print(get_description())

def get_description():
    return "more detail: https://github.com/necatiarslan/dynamodb-faker/blob/main/README.md "

if __name__ == '__main__':
    main()



