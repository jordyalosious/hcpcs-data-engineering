from datetime import datetime
from pathlib import Path
import subprocess

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator



PROJECT_ROOT = Path("/workspaces/hcpcs-data-engineering")

PROJECT_PYTHON = Path(
    "/home/codespace/.python/current/bin/python"
)




def run_script(script_path):
    

    full_path = PROJECT_ROOT / script_path

    print(f"Running: {full_path}")

    subprocess.run(
        [str(PROJECT_PYTHON), str(full_path)],
        cwd=str(PROJECT_ROOT),
        check=True,
    )


def extract_data():
    run_script("scraper/scraper.py")


def transform_data():
    run_script("transform/transform.py")


def load_data():
    run_script("database/load.py")


def validate_data():
    run_script("database/validation.py")


def notify_success():
    print("HCPCS pipeline completed successfully.")




with DAG(
    dag_id="hcpcs_data_pipeline",
    description="HCPCS data extraction, transformation, SCD2 loading and validation",
    start_date=pendulum.datetime(2026, 9, 1, tz="UTC"),
    schedule="@daily",
    catchup=False,
    tags=["hcpcs", "data-engineering", "etl"],
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract_data,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
    )

    load_task = PythonOperator(
        task_id="load_scd2",
        python_callable=load_data,
    )

    validate_task = PythonOperator(
        task_id="validation",
        python_callable=validate_data,
    )

    notify_task = PythonOperator(
        task_id="notify",
        python_callable=notify_success,
    )

    extract_task >> transform_task >> load_task >> validate_task >> notify_task