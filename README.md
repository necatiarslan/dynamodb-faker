# Dynamodb Faker
dynamodbfaker is a versatile Python package that empowers you to effortlessly create realistic but synthetic dynamodb data for a wide range of applications. If you need to generate test data for software development, this tool simplifies the process with an intuitive schema definition in YAML format.

### Key Features
**Schema Definition:** Define your target schema using a simple YAML file. Specify the structure of your table, attribute names and fake data generation code.

**Faker and Randomization:** Leverage the power of the Faker library and random data generation to create authentic-looking fake data that mimics real-world scenarios.

**Insert to Your Dynamodb Table:**
Insert generated data directly to your dynamodb table. 

### Installation
```bash 
pip install dynamodbfaker
```

### Sample Yaml File
```
version: 1
config:
  locale: en_US                       #faker locale Default:en_US
  on_update_item_error: RAISE_ERROR   #RAISE_ERROR, SKIP Default:RAISE_ERROR
  if_item_exists: OVERWRITE           #OVERWRITE, SKIP Default:OVERWRITE
  empty_table_first: False            #True/False Default:False
aws:
  region: us-east-1
  credentials_profile: default        #the profile name in your local .aws/config file Default:default
dynamodb_table:
  table_name: person
  row_count: 10000
  attributes:
    - name: id
      type: "N"
      data: row_id
    - name: first_name
      type: S
      data: fake.first_name()
    - name: last_name
      type: S
      data: fake.last_name()
    - name: age
      type: "N"
      data: fake.random_int(18, 90)
    - name: dob
      type: S
      data: fake.date_of_birth()
    - name: street_address
      type: S
      data: fake.street_address()
    - name: city
      type: S
      data: fake.city()
    - name: state_abbr
      type: S
      data: fake.state_abbr()
    - name: postcode
      type: S
      data: fake.postcode()
    - name: gender
      type: S
      data: random.choice(["male", "female"])
      null_percentage: 0.3
    - name: left_handed
      type: BOOL
      data: fake.pybool()
    - name: height
      type: "NULL"
```
[full yml example](tests/test_table.yaml)

### Sample Code
```python
import dynamodbfaker

# export in json format
dynamodbfaker.to_json("test_table.yaml", "./target_folder")

# you can use customer faker provider
from faker_education import SchoolProvider

dynamodbfaker.to_json("test_table.yaml", "./target_folder", fake_provider=SchoolProvider)
# multiple custom provider in list also works
```

### Sample CLI Command
You can use dynamodbfaker in your terminal for adhoc needs or shell script to automate fake data generation. \
Faker custom providers and custom functions are not supported in CLI.
```bash
# exports to current folder in json format
dynamodbfaker --config test_table.yaml

# exports to target folder in json format
dynamodbfaker --config test_table.yaml --target ./target_folder 

# exports to target file in json format 
dynamodbfaker --config test_table.yaml --target ./target_folder/target_file.json
```

### Sample JSON Output
```json
{
    "Items": [
        {
            "id": {
                "N": 1
            },
            "first_name": {
                "S": "Connie"
            },
            "last_name": {
                "S": "Skinner"
            },
            "age": {
                "N": 89
            },
            "dob": {
                "S": "1968-09-25"
            },
            "street_address": {
                "S": "5939 Christopher Crescent Apt. 747"
            },
            "city": {
                "S": "North Mistyside"
            },
            "state_abbr": {
                "S": "HI"
            },
            "postcode": {
                "S": "67235"
            },
            "gender": {
                "S": "male"
            },
            "left_handed": {
                "BOOL": true
            },
            "height": {
                "NULL": null
            }
        },
        {
            "id": {
                "N": 2
            },
            "first_name": {
                "S": "Carla"
            },
            "last_name": {
                "S": "Robles"
            },
            "age": {
                "N": 54
            },
            "dob": {
                "S": "1921-12-08"
            },
            "street_address": {
                "S": "35264 Jones Squares"
            },
            "city": {
                "S": "Michelleland"
            },
            "state_abbr": {
                "S": "TX"
            },
            "postcode": {
                "S": "94786"
            },
            "gender": {
                "S": "female"
            },
            "left_handed": {
                "BOOL": false
            },
            "height": {
                "NULL": null
            }
        }
    ],
    "Count": 2
}
```

### Custom Functions
With Dynamodb Faker, you have the flexibility to provide your own custom functions to generate column data. This advanced feature empowers developers to create custom fake data generation logic that can pull data from a database, API, file, or any other source as needed. You can also supply multiple functions in a list, allowing for even more versatility. The custom function you provide should return a single value, giving you full control over your synthetic data generation.

```python
from dynamodbfaker import dynamodbfaker
from faker import Faker

fake = Faker()
def get_level():
    return f"level {fake.random_int(1, 5)}"

dynamodbfaker.to_json("test_table.yaml", "./target_folder", custom_function=get_level)
```
Add get_level function to your yaml file
```
version: 1
config:
  locale: en_US #faker locale Default:en_US
  on_update_item_error: RAISE_ERROR #RAISE_ERROR, SKIP Default:RAISE_ERROR
  if_item_exists: OVERWRITE #OVERWRITE, SKIP Default:OVERWRITE
  empty_table_first: False #True/False Default:False
aws:
  region: us-east-1
  credentials_profile: default #the profile name in your local .aws/config file Default:default
dynamodb_table:
  table_name: person
  row_count: 10000
  attributes:
    - name: id
      type: "N"
      data: row_id
    - name: first_name
      type: S
      data: fake.first_name()
    - name: last_name
      type: S
      data: fake.last_name()
    - name: age
      type: "N"
      data: fake.random_int(18, 90)
    - column_name: level
      data: get_level() # custom function
```


### Faker Functions List
https://faker.readthedocs.io/en/master/providers.html#

### Bug Report & New Feature Request
https://github.com/necatiarslan/dynamodb-faker/issues/new 


### TODO
- Save to dynamodb


### Nice To Have
- 

Follow me on linkedin to get latest news \
https://www.linkedin.com/in/necati-arslan/

Thanks, \
Necati ARSLAN \
necatia@gmail.com


