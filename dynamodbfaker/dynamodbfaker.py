from . import config
from . import util
import pandas as pd
from faker import Faker
import random
from os import path

def to_target(file_type, config_file_path, target_file_path, table_name=None, **kwargs) -> {} :
    if file_type not in ["csv", "json", "excel", "parquet"]:
        raise Exception(f"Wrong file_type = {file_type}")
    
    result = {}
    df_dict = to_pandas(config_file_path, **kwargs)
    
    if path.isdir(target_file_path):
        for key_table_name in df_dict.keys():
            if table_name != None and key_table_name != table_name:
                continue #skip other tables

            df = df_dict[key_table_name]
            temp_file_path = path.join(target_file_path, util.get_temp_filename(key_table_name) + get_file_extension(file_type))
            call_export_function(df, file_type, temp_file_path)
            util.log(f"data is exported to {temp_file_path} as {file_type}")
            result[key_table_name] = temp_file_path 
    else:
        if table_name is None:
            table_name = list(df_dict.keys())[0]
        df = df_dict[table_name]
        df.to_csv(target_file_path)
        call_export_function(df, file_type, target_file_path)
        util.log(f"data is exported to {target_file_path} as {file_type}")
        result[table_name] = target_file_path
    
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

def call_export_function(data_frame: pd.DataFrame, file_type, target_file_path):
    if file_type == "csv":
        data_frame.to_csv(target_file_path, index=False)
    elif file_type == "json":
        data_frame.to_json(target_file_path, index=False, indent=4, orient='records', date_format='iso')
    elif file_type == "excel":
        data_frame.to_excel(target_file_path, index=False)
    elif file_type == "parquet":
        data_frame.to_parquet(target_file_path, index=False)
    else:
        raise Exception(f"Wrong file_type = {file_type}")

def to_csv(config_file_path, target_file_path=None, table_name=None, **kwargs) -> {} :
    if target_file_path is None:
        target_file_path = "."
    return to_target("csv", config_file_path, target_file_path, table_name, **kwargs)

def to_json(config_file_path, target_file_path=None, table_name=None, **kwargs) -> {} :
    if target_file_path is None:
        target_file_path = "."
    return to_target("json", config_file_path, target_file_path, table_name, **kwargs)

def to_excel(config_file_path, target_file_path=None, table_name=None, **kwargs) -> {} :
    if target_file_path is None:
        target_file_path = "."
    return to_target("excel", config_file_path, target_file_path, table_name, **kwargs)

def to_parquet(config_file_path, target_file_path=None, table_name=None, **kwargs) -> {} :
    if target_file_path is None:
        target_file_path = "."
    return to_target("parquet", config_file_path, target_file_path, table_name, **kwargs)

def to_pandas(config_file_path:str, **kwargs) -> pd.DataFrame:
    configurator = config.Config(config_file_path)
    tables = configurator.config["tables"]
    util.log(f"table count={len(tables)}")

    result = {}
    for table in tables:
        df = generate_table(table, configurator, **kwargs)
        result[table['table_name']] = df
    
    util.log(f"{len(result)} pandas dataframe(s) created")
    return result

def generate_table(table, configurator, **kwargs) -> pd.DataFrame:
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

    table_name = table['table_name']
    row_count = table['row_count']
    columns = table['columns']

    table_data = {}

    for column in columns:
        column_name = column['column_name']
        data_command = column['data']
        fake_data = generate_fake_data(faker, data_command, row_count, column, **kwargs)
        table_data[column_name] = fake_data
        #print(f"fake_data={fake_data}")

    df = pd.DataFrame(table_data)
    util.log(f"{table_name} pandas dataframe created")
    return df

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

        exec(f"result = {command}", variables)
        result = variables["result"]
        fake_data.append(result)

    return fake_data
