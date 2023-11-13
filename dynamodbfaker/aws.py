import boto3

def get_current_account_id():
    sts_client = boto3.client("sts")
    response = sts_client.get_caller_identity()
    account_id = response["Account"]
    return account_id

def get_current_region():
    session = boto3.Session()
    return session.region_name