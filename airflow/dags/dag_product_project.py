"""
Simple data pipeline taking data from source (API Request) and saving it to the target (PostgreSQL database)
after some transformations.
"""
import datetime as dt

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException

from airflow.operators.empty import EmptyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.http.sensors.http import HttpSensor

import logging
import requests
import pandas as pd

POSTGRES_CONN_ID = "yos_postgres"
TABLE_NAME = "count_feedbacks"
QUERY = "Наклейки для творчества"
API_URL = "https://search.wb.ru"
ENDPOINT = "/exactmatch/ru/common/v4/search?TestGroup=no_test&TestID=no_test&appType=1&curr=rub&dest=-1257786&query=" + \
      QUERY + "&resultset=catalog&sort=popular&spp=99&suppressSpellcheck=false"


@dag(
    start_date=dt.datetime(2024, 3, 11),
    schedule="20 16 * * *",
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": dt.timedelta(seconds=30),
    },
)
def product_project():

    start = EmptyOperator(task_id="start")

    create_count_table = PostgresOperator(
        task_id="create_count_table",
        postgres_conn_id=POSTGRES_CONN_ID,
        sql="""
            CREATE TABLE IF NOT EXISTS count_feedbacks (
                id TEXT,
                salepriceu INT,
                feedbacks INT,
                date DATE
            );
        """
    )

    is_api_available = HttpSensor(
        task_id="is_api_available",
        http_conn_id="product_api",
        endpoint=ENDPOINT
    )

    @task()
    def store_data(ds):
        r = requests.get(API_URL + ENDPOINT)

        if r.status_code == 200:
            logging.info("API is available.")

            r_json = r.json()
            product_count = len(r_json.get('data').get('products'))

            if product_count == 100:
                logging.info(f"The DAG run’s logical date is {ds}.")
                logging.info("API returns the list of 100 products.")

                r_df = pd.json_normalize(r_json, ['data', 'products'])[['id', 'salePriceU', 'feedbacks']]
                r_df['date'] = ds
                r_df = r_df.rename(columns={'salePriceU': 'salepriceu'})

                pg_hook = PostgresHook(POSTGRES_CONN_ID)
                engine = pg_hook.get_sqlalchemy_engine()
                r_df.to_sql("count_feedbacks", con=engine, if_exists="append", index=False)
                
                logging.info("Data was loaded successfully to DB.")
            else:
                logging.warning(f"Number of returned products is ONLY {product_count}.")
                raise AirflowException("Error in fetching data.")
        else:
            logging.warning(f"HTTP status {r.status_code}")
            raise AirflowException("API is not available.")
        
    end = EmptyOperator(task_id="end", trigger_rule="none_failed_min_one_success")

    start >> create_count_table >> is_api_available >> store_data() >> end
    
product_project()
    

