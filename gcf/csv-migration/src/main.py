import io
import json
import pandas as pd
from sqlalchemy import create_engine
from google.cloud import storage, secretmanager

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


def migrate_csv_to_db(bucket_name, file_name, table_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    csv_data = blob.download_as_text()

    with open("schemas.json", "r") as f:
        schema_json = json.load(f)
    
    column_names = list(schema_json[table_name].keys())

    data = pd.read_csv(io.StringIO(csv_data),header=None,names=column_names)

    engine = connect_database()
    data.to_sql(table_name, engine, if_exists="append", index=False)

def main(event, context=None):

    file_name = event["name"]
    bucket_name = event["bucket"]

    with open("files_mapping.json", "r") as f:
        files_mapping = json.load(f)

    if file_name in list(files_mapping.keys()):
        migrate_csv_to_db(bucket_name, file_name, files_mapping[file_name])


def main_local():

    event = {
        "name": "jobs.csv",
        "bucket": "data-bjvc-test"
    }

    file_name = event['name']
    bucket_name = event['bucket']

    with open("files_mapping.json", "r") as f:
        files_mapping = json.load(f)

    if file_name in list(files_mapping.keys()):
        migrate_csv_to_db(bucket_name, file_name, files_mapping[file_name])


if __name__ == "__main__":
    main_local()
