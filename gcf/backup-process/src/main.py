import io
import fastavro
import pandas as pd
from google.cloud import storage, secretmanager
from datetime import datetime
import json
from sqlalchemy import create_engine, text
import functions_framework


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


def backup_to_avro(table_name,timestamp):

    with open("schemas.json", "r") as f:
        schema_json = json.load(f)

    schema_table = schema_json[table_name]

    avro_schema = {
        "type": "record",
        "name": table_name,
        "fields": [{"name": col_name, "type": "string" if col_type == "str" else col_type} for col_name,col_type in schema_table.items()],
    }

    try:
        engine = connect_database()
        df = pd.read_sql_table(table_name, engine)
    except Exception as e:
        print("Error:", e)
    finally:
        if engine:
            engine.dispose()

    # Complete NaN values
    for k,v in schema_table.items():
        col_name = k
        col_type = v
        if col_type == "int":
            df[k].fillna(-1, inplace=True)
            df[k] = df[k].astype(int)

        if col_type == "str":
            df[k].fillna("Null", inplace=True)

    # Convert the DataFrame to a list of dictionaries
    records = df.to_dict(orient='records')

    # Serialize the records to Avro format
    avro_buffer = io.BytesIO()
    fastavro.writer(avro_buffer, avro_schema, records)
    avro_buffer.seek(0)

    # Set up the Google Cloud Storage client
    bucket_name = 'artifacts-bjvc-test'
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)

    # Upload the Avro file to Google Cloud Storage
    blob = bucket.blob(f"backups/{table_name}_{timestamp}.avro")
    blob.upload_from_file(avro_buffer, content_type="application/octet-stream")

    print(f"Table {table_name} backup sucessfully")

@functions_framework.http
def main(request):

    request_json = request.get_json(silent=True)
    if request_json["key"] == "exec":

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Connection
        engine = connect_database()

        # Define a query to list all tables in the database
        query = text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)

        try:
            with engine.connect() as connection:
                result = connection.execute(query)
                list_tables = [row[0] for row in result]
        except Exception as e:
            print("Error:", e)
        finally:
            if engine:
                engine.dispose()

        for table_name in list_tables:
            backup_to_avro(table_name,timestamp)

        return "Backup finished sucessfully",200

    else:

        return "Bad request",400

