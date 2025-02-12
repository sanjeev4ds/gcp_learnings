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
    dag_id = "GCS_to_BQ_and_AGG_Refined",
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
        source_objects = ["sample_csv.csv"],
        destination_project_dataset_table= "sanjeevyoutubefirstapi.airflow_destination.airflow_table_refined",
        schema_fields = [
            {'name': 'col1', 'type':'INTEGER', 'mode':'NULLABLE'},
            {'name': 'col2', 'type': 'STRING', 'mode': 'NULLABLE'},
            {'name': 'col3', 'type': 'INTEGER', 'mode': 'NULLABLE'}
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
                "query": "create or replace table sanjeevyoutubefirstapi.airflow_destination.airflow_table_refined_2 as select col2, sum(col3) as count from sanjeevyoutubefirstapi.airflow_destination.airflow_table_refined group by col2",
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