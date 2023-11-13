import boto3
from . import util
from . import config

def get_dynamodb_client():
    region = config.Config.get_current().get_region()

    if region != None:
        dynamodb = boto3.client("dynamodb", region_name=region)
    else:
        dynamodb = boto3.client("dynamodb", region_name=region)

    return dynamodb

def put_item(table_name, item, dynamodb_client=None):
    if dynamodb_client is None:
        dynamodb_client = get_dynamodb_client()
    
    response = dynamodb_client.put_item(
        TableName = table_name,
        Item = item
    )

    return response