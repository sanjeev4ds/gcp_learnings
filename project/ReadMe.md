# project contains

## cloud composer
- connection: http_connection_id to link domain
- EmptyOperator: For dummy start and end
- SimpleHttpOperator : To extract data from http url
- PythonOperator1 :
  - Read locales file from gcs location
  - To transform the data and extract required information (level 1)
  - Dump half data half to GCS again
  - pull from xcom and push another transformation to xcom again
- PythonOperator2: read data from xcom (http values and 
- BashOperator: To set environment variables in airflow environment
- GCSToBigQueryOperator: level one transformation (reading data from gcs and dumping directly to BigQuery)
- Crea
