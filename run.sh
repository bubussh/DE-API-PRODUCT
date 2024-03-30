#!/usr/bin/env bash

brew services start postgresql@16
sleep 4

export AIRFLOW_HOME=~/api-product-project/airflow
export no_proxy=*

airflow standalone