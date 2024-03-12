from distutils.log import Log
from faker import Faker
import random
import json
from os import path
import datetime, time
from . import config, util, dynamodb

def to_target(file_type, config_file_path, target_file_path, **kwargs) -> str :
    if file_type not in ["json"]:
        raise Exception(f"Wrong file_type = {file_type}")
    
    item_list = get_item_list(config_file_path, **kwargs)
    
    json_data = { "Items" : item_list, "Count" : len(item_list)}

    if path.isdir(target_file_path):
            temp_file_path = path.join(target_file_path, util.get_temp_filename() + util.get_file_extension(file_type))
            call_export_function(json_data, temp_file_path)
            util.log(f"data is exported to {temp_file_path} as {file_type}")
            result = temp_file_path 
    else:
        call_export_function(json_data, target_file_path)
        util.log(f"data is exported to {target_file_path} as {file_type}")
        result = target_file_path
    
    return result

def call_export_function(json_data, target_file_path):
    with open(target_file_path, mode="w") as file:
        json.dump(json_data, file, indent=4)

def to_json(config_file_path, target_file_path=None, **kwargs) -> str :
    if target_file_path is None:
        target_file_path = "."
    return to_target("json", config_file_path, target_file_path, **kwargs)

def to_dynamodb(config_file_path, target_file_path=None, **kwargs):
    configurator = config.Config(config_file_path)
    item_list = get_item_list(config_file_path, **kwargs)
    table_name = configurator.get_table()
    batch = configurator.get_batch()
    sleep = configurator.get_sleep()
    region = configurator.get_region()
    dynamodb_client = dynamodb.get_dynamodb_client()
    on_item_insert_error = configurator.get_on_item_insert_error()

    iteration = 1
    items_inserted = 0
    for item in item_list:
        util.progress_bar(iteration, len(item_list), "Inserting Dynamodb")
        try:
            dynamodb.put_item(table_name, item, dynamodb_client=dynamodb_client)
            items_inserted += 1
            if sleep > 0 and items_inserted % batch == 0:
                time.sleep(sleep / 1000)
        except Exception as e:
            if on_item_insert_error == "RAISE_ERROR":
                raise Exception(f"Dynamodb Table {table_name} put_item error !!!\n{item}\n{e}")
        
        iteration += 1
    
    util.log(f"{items_inserted} item(s) inserted to {table_name} dynamodb table")

    if target_file_path != None:
        file_type = "json"
        json_data = { "Items" : item_list, "Count" : len(item_list)}
        
        if path.isdir(target_file_path):
            target_file_path = path.join(target_file_path, util.get_temp_filename(table_name) + util.get_file_extension(file_type))
        
        call_export_function(json_data, target_file_path)
        util.log(f"data is exported to {target_file_path} as {file_type}")

def get_item_list(config_file_path:str, **kwargs):
    configurator = config.Config(config_file_path)

    locale = None
    if "config" in configurator.config and "locale" in configurator.config["config"]:
        locale = configurator.get_locale()

    faker = Faker(locale)

    if "fake_provider" in kwargs:
        if not isinstance(kwargs["fake_provider"], list):
            faker.add_provider(kwargs["fake_provider"])
        else:
            for provider in kwargs["fake_provider"]:
                faker.add_provider(provider)

    table_name = configurator.get_table()
    row_count = configurator.get_rowcount()
    attribute_list = configurator.get_attributes()
    python_import = configurator.get_python_import()

    json_data = {}
    iteration = 1
    for attr in attribute_list:
        attr_name = attr["name"]
        if "data" in attr:
            data_command = attr["data"]
        else:
            data_command = "fake.word()"

        util.progress_bar(iteration, len(attribute_list), f"Generating {attr_name}")

        fake_data = generate_fake_value_list(faker, data_command, row_count, attr, python_import, json_data, **kwargs)
        json_data[attr_name] = fake_data

        iteration += 1

    items = []
    iteration = 1
    for row in range(row_count):
        util.progress_bar(iteration, row_count, "Shaping JSON")
        item = {}
        for attr in attribute_list:
            attr_name = attr["name"]
            attr_data = json_data[attr_name][row]
            attr_type, attr_value = get_attribute_type_value(attr_data, table_name, attr_name)
            
            item[attr_name] = { attr_type : attr_value }

        items.append(item)

        iteration += 1

    util.log(f"{table_name} fake data created")
    return items

def get_attribute_type_value(data, table_name, attr_name):
    if isinstance(data, str):
        return "S", data
    elif isinstance(data, bool):
        return "BOOL", data
    elif isinstance(data, int) or isinstance(data, float):
        return "N", str(data)
    elif data is None:
        return "NULL", True
    else:
        raise Exception(f"Attribute type can not be infered {table_name}/{attr_name}")

def generate_fake_value_list(fake: Faker, command, row_count, attribute_config, python_import, json_data, **kwargs):
    result = None
    
    attribute_name = attribute_config["name"]

    null_percentge = 0
    null_indexies = []
    if "null_percentage" in attribute_config:
        null_percentge = util.parse_null_percentge(attribute_config["null_percentage"])
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
        
        if python_import and isinstance(python_import, list):
            for library_name in python_import:
                variables[library_name] = __import__(library_name)

        for key in json_data:
            variables[key] = json_data[key][row_id-1]

        try:
            exec(f"result = {command}", variables)
            result = variables["result"]
        except Exception as e:
            util.log(f"Data Generation Error Name:{attribute_name} Command: {command}")
            raise e

        if isinstance(result, (datetime.date, datetime.datetime)):
            result = result.isoformat()

        fake_data.append(result)

    return fake_data
