import io
import pandas as pd
from fastavro import reader
import functions_framework
import json
from google.cloud import storage, secretmanager
from sqlalchemy import create_engine, text


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

def find_avro_file(bucket_name, path, table_name):

    gcs_client = storage.Client()
    bucket = gcs_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=path)

    avro_file_name = None
    max_creation_date = None
    # Add Try Exception to validate if files exists
    for blob in blobs:
        file_name = blob.name[len(path):] if blob.name.startswith(path) else blob.name
        if file_name.startswith(table_name) and (max_creation_date is None or blob.time_created > max_creation_date):
            max_creation_date = blob.time_created
            avro_file_name = file_name

    return avro_file_name


@functions_framework.http
def main(request):

    request_json = request.get_json(silent=True)

    with open("schemas.json", "r") as f:
        schema_json = json.load(f)

    list_tables = []
    for k in schema_json.keys():
        list_tables.append(k)

    if request_json["table_name"] in list_tables:

        bucket_name = "artifacts-bjvc-test"
        avro_path = "backups/"
        table_name = request_json["table_name"]
        avro_file_name = find_avro_file(bucket_name, avro_path, table_name)
        avro_file_path = avro_path + avro_file_name

        gcs_client = storage.Client()
        bucket = gcs_client.get_bucket(bucket_name)

        blob = storage.Blob(avro_file_path, bucket)
        file_contents = blob.download_as_bytes()

        avro_reader = reader(io.BytesIO(file_contents))

        schema = avro_reader.writer_schema
        records = list(avro_reader)

        df = pd.DataFrame(records)

        engine = connect_database()

        try:
            with engine.begin() as connection:
                connection.execute(text(f"TRUNCATE TABLE {table_name}"))

            df.to_sql(table_name, engine, if_exists='append', index=False)

            return f"The table {table_name} has been restored sucessfully", 200

        except Exception as e:
            print("Error:", e)
            return f"Fail query execution", 400
        finally:
            if engine:
                engine.dispose()
    
    else:
        return "Bad request", 400
