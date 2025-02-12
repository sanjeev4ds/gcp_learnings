from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.operators.python import PythonOperator
import json
import os
from datetime import datetime, timedelta
from google.cloud import storage
from more_itertools.more import bucket
from google.oauth2 import service_account

yesterday = datetime.combine(datetime.today() - timedelta(1), datetime.min.time())

# Path to your service account key file
key_path = '/Users/sanjeevsaini/PycharmProjects/pythonProject/gcp_cloudcomposer/sanjeevyoutubefirstapi-ac7e25988110.json'


def WriteToGcs(ti):
    data = ti.xcom_pull(task_ids=["get_http_data"])
    print("data before")
    print(data)
    data = list(data)
    print(data)
    json_data = json.dumps(data
                           )
    print(json_data)
    print("data after")
    bucket_name = "cloud_composer_learning"
    destination_blob_name = "sample.json"
    # Create credentials from the service account key file
    credentials = service_account.Credentials.from_service_account_file(key_path)
    # Initialize the storage client with the credentials
    storage_client = storage.Client(credentials=credentials, project=credentials.project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(str(json_data))
    print(f"{destination_blob_name} with contents upload to {bucket_name}")

dag = DAG(
    dag_id= "demo_http_operator_demo",
    default_args = {"retries":1},
    tags= ["example"],
    start_date= yesterday,
    catchup=False
)

get_http_data = SimpleHttpOperator(
    task_id= "get_http_data",
    http_conn_id= "http_conn_id_demo",
    method = "GET",
    endpoint = "/objects",
    response_filter= lambda response : json.loads(response.text),
    dag = dag
)

write_data_to_gcs = PythonOperator(
    task_id= "write_data_to_gcs",
    python_callable=WriteToGcs
)

get_http_data>>write_data_to_gcs