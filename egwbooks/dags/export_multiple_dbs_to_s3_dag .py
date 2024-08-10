from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import sqlite3
import pandas as pd
import boto3
from io import StringIO
from keys import get_s3_credentials 

# Get AWS credentials
credentials = get_s3_credentials()
aws_access_key_id = credentials['aws_access_key_id']
aws_secret_access_key = credentials['aws_secret_access_key']
s3_bucket = credentials['bucket_name']

s3_client = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)

# Function to extract data from SQLite and upload to S3
def extract_and_upload_to_s3(db_name, table_name, s3_key):
    # Define the path for the database
    db_path = f'/opt/airflow/dags/{db_name}'
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    
    # Save DataFrame to a CSV in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)  # Move to the start of the StringIO buffer
    
    s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=csv_buffer.getvalue())
    
    conn.close()


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'retries': 1,
}


with DAG(
    'export_multiple_dbs_to_s3_dag',
    default_args=default_args,
    description='A DAG to export multiple SQLite databases to S3',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    dbs = [
        {'db_name': 'orders.db', 'table_name': 'orders', 's3_key': 'orders.csv'},
        {'db_name': 'egw.db', 'table_name': 'Books', 's3_key': 'egw.csv'},
        {'db_name': 'feedback.db', 'table_name': 'feedback', 's3_key': 'feedback.csv'},
        {'db_name': 'users.db', 'table_name': 'users', 's3_key': 'users.csv'},
    ]

    tasks = []

    for db in dbs:
        task = PythonOperator(
            task_id=f'extract_and_upload_{db["s3_key"].split("/")[-1].replace(".csv", "")}',
            python_callable=extract_and_upload_to_s3,
            op_args=[db['db_name'], db['table_name'], db['s3_key']],
        )
        tasks.append(task)

    # We start from the second task because the first one doesnt have a previos task to wait on
    for i in range(1, len(tasks)):
        tasks[i-1] >> tasks[i]
