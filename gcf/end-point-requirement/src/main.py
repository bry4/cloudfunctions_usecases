import os
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text
import functions_framework
from google.cloud import secretmanager
import json

app = Flask(__name__)

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

def query_db(query):

    engine = connect_database()
    with engine.connect() as connection:
        result_proxy = connection.execute(query)
        column_names = result_proxy.keys()
        results = [
            {column: value for column, value in zip(column_names, row)}
            for row in result_proxy
        ]
    return results


@app.route("/requirement1")
def requirement1():
    query = text("""select
        d.department,
        j.job,
        sum(case when extract(quarter from cast(h.datetime as timestamp)) = 1 then 1 else 0 end) as Q1,
        sum(case when extract(quarter from cast(h.datetime as timestamp)) = 2 then 1 else 0 end) as Q2,
        sum(case when extract(quarter from cast(h.datetime as timestamp)) = 3 then 1 else 0 end) as Q3,
        sum(case when extract(quarter from cast(h.datetime as timestamp)) = 4 then 1 else 0 end) as Q4
    from
        hired_employees h
    left join
        departments d on h.department_id = d.id
    left join
        jobs j on h.job_id = j.id
    where 
        h.datetime != 'Null' and
        extract(year from cast(h.datetime as timestamp)) = 2021
    group by 
        d.department,
        j.job
    order by 
        d.department asc,
        j.job asc;""")
    results = query_db(query)
    return jsonify(results)

@app.route("/requirement2")
def requirement2():
    query = text("""select
        dh.department_id as id,
        dh.department as department,
        dh.num_employees as hired
    from (
        select
            d.id as department_id,
            d.department,
            count(h.id) as num_employees
        from
            hired_employees h
        join
            departments d on h.department_id = d.id
        where
            h.datetime != 'Null' and
            extract(YEAR from cast(h.datetime as timestamp)) = 2021
        group by
            d.id,
            d.department
    ) as dh,
    (
        select
            avg(num_employees) as mean_hires
        from (
            select
                d.id as department_id,
                d.department,
                count(h.id) as num_employees
            from
                hired_employees h
            join
                departments d on h.department_id = d.id
            where
                h.datetime != 'Null' and
                extract(YEAR from cast(h.datetime as timestamp)) = 2021
            group by
                d.id,
                d.department
        ) as temp
    ) as mh
    where
        dh.num_employees > mh.mean_hires
    ORDER BY
        dh.num_employees desc;
    """)
    results = query_db(query)
    return jsonify(results)

@functions_framework.http
def main(request):
    with app.test_request_context(request.url):
        try:
            response = app.dispatch_request()
            return (response.get_data(), response.status_code, response.headers)
        except Exception as e:
            app.logger.exception(e)
            return (str(e), 500, {})
