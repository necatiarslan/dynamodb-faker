from . import config
from . import util
from faker import Faker
import random
import json
from os import path
import datetime

def to_target(file_type, config_file_path, target_file_path, boto_session=None, **kwargs) -> {} :
    if file_type not in ["json"]:
        raise Exception(f"Wrong file_type = {file_type}")
    
    json_data = to_json_data(config_file_path, boto_session=None, **kwargs)
    
    if path.isdir(target_file_path):
            temp_file_path = path.join(target_file_path, util.get_temp_filename() + get_file_extension(file_type))
            call_export_function(json_data, temp_file_path)
            util.log(f"data is exported to {temp_file_path} as {file_type}")
            result = temp_file_path 
    else:
        call_export_function(json_data, target_file_path)
        util.log(f"data is exported to {target_file_path} as {file_type}")
        result = target_file_path
    
    return result

def get_file_extension(file_type):
    if file_type == "csv":
        return ".csv"
    elif file_type == "json":
        return ".json"
    elif file_type == "parquet":
        return ".parquet"
    elif file_type == "excel":
        return ".xlsx"
    else:
        return ".txt"

def call_export_function(json_data, target_file_path):
    with open(target_file_path, mode="w") as file:
        json.dump(json_data, file, indent=4)

def to_json(config_file_path, target_file_path=None, boto_session=None, **kwargs) -> {} :
    if target_file_path is None:
        target_file_path = "."
    return to_target("json", config_file_path, target_file_path, boto_session, **kwargs)

def to_json_data(config_file_path:str, boto_session=None, **kwargs) -> {}:
    configurator = config.Config(config_file_path)

    df = generate_table(configurator, boto_session, **kwargs)
    
    util.log(f"pandas dataframe created")
    return df

def generate_table(configurator, boto_session=None, **kwargs) -> {}:
    locale = None
    if "config" in configurator.config and "locale" in configurator.config["config"]:
        locale = configurator.config["config"]["locale"]

    faker = Faker(locale)

    if "fake_provider" in kwargs:
        if not isinstance(kwargs["fake_provider"], list):
            faker.add_provider(kwargs["fake_provider"])
        else:
            for provider in kwargs["fake_provider"]:
                faker.add_provider(provider)

    table_name = configurator.config['dynamodb_table']["table_name"]
    row_count = configurator.config['dynamodb_table']['row_count']
    columns = configurator.config['dynamodb_table']["attributes"]

    table_data = {}

    for column in columns:
        column_name = column['name']
        column_type = column["type"]
        if column_type == "NULL":
            data_command = "NULL"
        else:
            data_command = column['data']
        fake_data = generate_fake_data(faker, data_command, row_count, column, **kwargs)
        table_data[column_name] = { column_type : fake_data }
        #print(f"fake_data={fake_data}")

    util.log(f"{table_name} fake data created")
    return table_data

def parse_null_percentge(null_percentage):
    if isinstance(null_percentage, str) and null_percentage[-1] == "%":
        null_percentage = float(null_percentage[0:-1])
    
    if isinstance(null_percentage, str) and null_percentage[0] == "%":
        null_percentage = float(null_percentage[1:])

    if isinstance(null_percentage, int) or isinstance(null_percentage, float):
        if null_percentage >= 0 and null_percentage <= 1:
            return float(null_percentage)
        elif null_percentage >= 0 and null_percentage<= 100:
            return float(null_percentage / 100)

    return float(0)

def generate_fake_data(fake: Faker, command, row_count, column_config, **kwargs) -> []:
    result = None
    
    null_percentge = 0
    null_indexies = []
    if "null_percentage" in column_config:
        null_percentge = parse_null_percentge(column_config["null_percentage"])
        for _ in range(1, int(row_count * null_percentge)+1):
            random_num = random.randint(1, row_count)
            null_indexies.append(random_num)


    fake_data = []
    for row_id in range(1, row_count+1):
        if row_id in null_indexies:
            fake_data.append(None) #add null data
            continue

        variables = {
            "random": random,
            "fake": fake,
            "result": result,
            "command": command,
            "row_id": row_id
            }
        
        if "custom_function" in kwargs:
            if isinstance(kwargs["custom_function"], list):
                for func in kwargs["custom_function"]:
                    variables[func.__name__] = func
            else:
                func = kwargs["custom_function"]
                variables[func.__name__] = func
        if command == "NULL":
            result = "NULL"
        else:
            exec(f"result = {command}", variables)
        result = variables["result"]

        if isinstance(result, (datetime.date, datetime.date)):
            result = result.isoformat()

        fake_data.append(result)

    return fake_data
