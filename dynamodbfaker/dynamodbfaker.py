from . import config
from . import util
from faker import Faker
import random
import json
from os import path
import datetime

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

def get_item_list(config_file_path:str, **kwargs) -> []:
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

    json_data = {}
    iteration = 1
    for attr in attribute_list:
        attr_name = attr["name"]
        attr_type = attr["type"]
        if attr_type == "NULL":
            data_command = "NULL"
        else:
            data_command = attr['data']

        util.progress_bar(iteration, len(attribute_list), f"Generating {attr_name}")

        fake_data = generate_fake_value_list(faker, data_command, row_count, attr, **kwargs)
        json_data[attr_name] = fake_data

        iteration += 1

    items = []
    iteration = 1
    for row in range(row_count):
        util.progress_bar(iteration, row_count, "Shaping JSON")
        item = {}
        for attr in attribute_list:
            attr_name = attr["name"]
            attr_type = attr["type"]
            attr_data = json_data[attr_name][row]
            
            if attr_data is None:
                item[attr_name] = { "NULL" : True }
            else:
                item[attr_name] = { attr_type : attr_data }

        items.append(item)

        iteration += 1

    util.log(f"{table_name} fake data created")
    return items

def generate_fake_value_list(fake: Faker, command, row_count, attribute_config, **kwargs) -> []:
    result = None
    
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
        if command == "NULL":
            result = "NULL"
        else:
            exec(f"result = {command}", variables)
        result = variables["result"]

        if isinstance(result, (datetime.date, datetime.date)):
            result = result.isoformat()

        fake_data.append(result)

    return fake_data
