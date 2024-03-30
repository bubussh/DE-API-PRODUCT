"""
Data pipeline for dynamic computing the number of new feedbacks per day.
"""
import datetime as dt

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException

from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

import logging

POSTGRES_CONN_ID = "yos_postgres"
SOURCE_TABLE_NAME = "count_feedbacks"


@dag(
    start_date=dt.datetime(2024, 3, 11),
    schedule="25 16 * * *",
    catchup=True,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": dt.timedelta(seconds=30),
    },
)
def dynamic_feedback():

    start = EmptyOperator(task_id="start")

    create_dynamic_table = PostgresOperator(
        task_id="create_dynamic_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="""
            CREATE TABLE IF NOT EXISTS dynamic_feedbacks (
                date DATE,
                id TEXT,
                new_feedbacks INT
            );
        """
    )

    @task
    def validate_data_in_source_table(**context):
        """Check arrival of actual data in source table."""
        ds_date = context["ds"]
        pg_hook = PostgresHook(POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        logging.info(f"ds {ds_date}")
        validation_query = f"SELECT * FROM {SOURCE_TABLE_NAME} WHERE DATE = '{ds_date}';"

        cursor.execute(validation_query)
        row_count = cursor.rowcount

        if row_count == 0:
            logging.warning("New data is not present in source table.")
            raise AirflowException("Error in validating data.")
        else:
            logging.info("New data is present in source table.")

    upload_new_data = PostgresOperator(
        task_id="upload_new_data",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="sql/query.sql"
    )
    
    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    start >> create_dynamic_table >> validate_data_in_source_table() >> upload_new_data >> end
    
dynamic_feedback()
    