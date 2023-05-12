import functions_framework
import json
import pandas as pd
from sqlalchemy import create_engine
from google.cloud import secretmanager

def connect_database():

    json_secrets = get_secret("400290530696","test_db")
    DB_USER = json_secrets["DB_USER"]
    DB_PASS = json_secrets["DB_PASS"]
    DB_HOST = json_secrets["DB_HOST"]
    DB_NAME = json_secrets["DB_NAME"]
    database_connection_string = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(database_connection_string)

    return engine

def get_secret(project_id, secret_name, version="latest"):
    
    client = secretmanager.SecretManagerServiceClient()
    secret_version_name = f"projects/{project_id}/secrets/{secret_name}/versions/{version}"
    response = client.access_secret_version(request={"name": secret_version_name})
    secret_value = response.payload.data.decode("UTF-8")
    
    return json.loads(secret_value)

def validate_data(data_values,table_name):

    with open("schemas.json", "r") as f:
        table_columns = json.load(f)
    
    columns = table_columns[table_name]

    column_type_mapping = {
        "int":int,
        "str":str
    }

    validate_columns = {k: column_type_mapping[v] for k, v in columns.items()}

    for row in data_values:
        # Check table structure
        if set(row.keys()) != set(validate_columns.keys()):
            return False, "Data structure doesn't match the target table."

        # Check data types and non-null values for "id"
        for column, value in row.items():
            if not isinstance(value, validate_columns[column]):
                return False, f"Invalid data type for '{column}'. Expected {validate_columns[column].__name__}."
            if column == "id" and value is None:
                return False, "The 'id' column must have a non-null value."

    return True, "Data validated sucessfully"


@functions_framework.http
def main(request):
    request_json = request.get_json(silent=True)
    table_name = request_json["table"]
    data_values = request_json["values"]
    mode = request_json["mode"]

    is_valid,msg_valid = validate_data(data_values,table_name)

    if not is_valid:
        return msg_valid, 400

    engine = connect_database()

    try:

        data = pd.DataFrame(data_values)
        data.to_sql(table_name, engine, if_exists=mode, index=False)

        return "Data inserted successfully", 201

    except Exception as e:

        print(f"Error inserting data: {str(e)}")
        return "Error inserting data", 400

