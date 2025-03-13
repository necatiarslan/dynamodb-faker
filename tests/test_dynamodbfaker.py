import sys, os, shutil
sys.path.append(os.path.abspath("."))

from dynamodbfaker import dynamodbfaker
from faker_education import SchoolProvider
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

directory_path = 'tests/exports'
if os.path.isdir(directory_path):
    shutil.rmtree(directory_path)
    os.mkdir(directory_path)

os.system('clear')
dynamodbfaker.to_json("tests/test_table.yaml", "./tests/exports", fake_provider=SchoolProvider, custom_function=get_level)
#dynamodbfaker.to_dynamodb("tests/test_table.yaml")
