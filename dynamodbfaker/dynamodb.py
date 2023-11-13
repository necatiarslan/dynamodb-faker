import boto3
from . import util

def get_dynamodb_client(region_name):
    dynamodb = boto3.client("dynamodb", region_name=region_name)
    return dynamodb

def put_item(table_name, item, region_name=None, dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = get_dynamodb_client(region_name)
    
    response = dynamodb_client.put_item(
        TableName = table_name,
        Item = item
    )

    return response