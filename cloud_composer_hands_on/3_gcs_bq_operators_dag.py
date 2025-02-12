import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

#yesterday date value
yesterday = datetime.combine(datetime.today() - timedelta(1), datetime.min.time())

default_args = {
    "start_date": yesterday,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes= 5)
}

with DAG(
    dag_id = "GCS_to_BQ_and_AGG",
    catchup= False,
    schedule_interval = timedelta(days =1),
    default_args= default_args
) as dag:

    start = EmptyOperator(
        task_id="start",
        dag = dag
    )

    gcs_to_bq_load = GCSToBigQueryOperator(
        task_id = "gcs_to_bq_load",
        bucket = "cloud_composer_learning",
        source_objects = ["USA_cars_datasets.csv"],
        destination_project_dataset_table= "sanjeevyoutubefirstapi.airflow_destination.airflow_table",
        schema_fields = [
            {'name': 'index', 'type':'INTEGER', 'mode':'NULLABLE'},
            {'name': 'price', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'brand', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'model', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'year', 'type': 'INTEGER', 'mode': 'NULLABLE'},

            {'name': 'title_status', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'mileage', 'type': 'INTEGER', 'mode': 'NULLABLE'},
            {'name': 'color', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'vin', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'lot', 'type': 'INTEGER', 'mode': 'NULLABLE'},

            {'name': 'state', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'country', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'condition', 'type': 'STRING', 'mode': 'NULLABLE'}
        ],
        source_format= 'CSV',
        field_delimiter= ',',
        skip_leading_rows= 1,
        create_disposition= 'CREATE_IF_NEEDED',
        write_disposition= 'WRITE_TRUNCATE',
        gcp_conn_id='google_cloud_default',
        # bigquery_conn_id= 'google_cloud_default',
        # google_cloud_storage_conn_id= 'google_cloud_default',
        dag= dag
    )

    create_agg_bq_table = BigQueryInsertJobOperator(
        task_id="create_aggr_bq_table",
        configuration={
            "query":{
                "query": "create or replace table sanjeevyoutubefirstapi.airflow_destination.airflow_table_2 as select year, count(*) as count from sanjeevyoutubefirstapi.airflow_destination.airflow_table group by year",
                "useLegacySql": False,
                "priority": "BATCH"
            }
        },  # Pass the missing configuration parameter if needed
        gcp_conn_id='google_cloud_default',
        dag= dag
    )

    end = EmptyOperator(
        task_id="end",
        dag=dag
    )

start>>gcs_to_bq_load>>create_agg_bq_table>>end