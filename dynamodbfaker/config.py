import yaml
from os import path
from . import util

class Config:
    def __init__(self, file_path):
        if not path.isabs(file_path):
            file_path = path.abspath(file_path)

        util.log(f"received config is {file_path}")
        self.file_path = file_path
        self.load_config_file()
        self.validate_config()
    
    def load_config_file(self):
        if path.isfile(self.file_path):
            with open(self.file_path, "r") as file:
                self.config = yaml.safe_load(file)
        else:
            raise Exception(f"{self.file_path} file not found")
    
    def validate_config(self):
        if "dynamodb_table" not in self.config:
            raise Exception(f"Config file should have dynamodb_table node")
        
        dynamodb_table = self.config["dynamodb_table"]
        if "table_name" not in dynamodb_table:
            raise Exception(f"Table should have a table_name node")
        
        table_name = dynamodb_table["table_name"]

        if "row_count" not in dynamodb_table:
            raise Exception(f"{table_name} table should have a row_count node")

        if "attributes" not in dynamodb_table:
            raise Exception(f"{table_name} table should have a attributes node")

        if len(dynamodb_table["attributes"]) == 0:
            raise Exception(f"{table_name} table should have at least 1 attribute")
        
        for attribute in dynamodb_table["attributes"]:
            if "name" not in attribute:
                raise Exception(f"{table_name} table have an attribute without a name")
        
            attr_name = attribute["name"]
            
            if "type" not in attribute:
                raise Exception(f"{table_name} table {attr_name} attribute do not have a type node")
            
            type = attribute["type"]

            if type not in Config.get_supported_data_types():
                raise Exception(f"{table_name} table {attr_name} attribute type {type} is not supported yet :-() use {Config.get_supported_data_types()}")

            if type != "NULL" and "data" not in attribute:
                raise Exception(f"{table_name} table {attr_name} {attribute['type']} attribute do not have a data node")
        
        util.log(f"config file is validated")

    def get_supported_data_types():
        return ["S", "N", "BOOL", "NULL"]

    def get_locale(self):
        return self.config["config"]["locale"]

    def get_table(self):
        return self.config['dynamodb_table']["table_name"]

    def get_rowcount(self):
        return self.config['dynamodb_table']['row_count']
    
    def get_attributes(self):
        return self.config['dynamodb_table']["attributes"]
