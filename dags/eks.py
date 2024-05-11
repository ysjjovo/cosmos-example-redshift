import os
import boto3
import json
from datetime import datetime
from pathlib import Path

from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator

from cosmos.providers.dbt import DbtTaskGroup


@dag(
    schedule_interval="@daily",
    start_date=datetime(2023, 7, 24),
    catchup=False,
)
def basic_eks_cosmos_task_group() -> None:
   
    pre_dbt = EmptyOperator(task_id="pre_dbt")


    _project_dir= "/usr/local/airflow/dags/dbt/jaffle_shop/"

    redshift_dbt_group = DbtTaskGroup(
        dbt_root_path=_project_dir,
        dbt_project_name="dbtcicd",
        execution_mode="kubernetes",
        conn_id="redshift-default",
        operator_args={
            "do_xcom_push": False,
            "project_dir":"/app/dags/dbt/jaffle_shop/",
            "namespace":"prod-bigdata-dw-mwaa",
            "image": "139260835254.dkr.ecr.us-east-2.amazonaws.com/dbt-jaffle-shop-redshift:1.0.0",
            "get_logs": True,
            "is_delete_operator_pod": True,
            "name": "mwaa-cosmos-pod-dbt",
            "config_file": "/usr/local/airflow/dags/kubeconfig",
            "in_cluster": False,
            "vars": '{"my_car": "val1"}',
            "env_vars": {
                "TARGT": "dev",
                "HOST": 'lin.cxylowtpy724.us-east-2.redshift.amazonaws.com', 
                "PORT": '5439',
                "USER": 'admin',
                "PASSWORD": '',
                "DATABASE": 'dev',
                "SCHEMA": 'public',
            },
            "image_pull_policy": "Always",
        },
    )

    post_dbt = EmptyOperator(task_id="post_dbt")

    pre_dbt >> redshift_dbt_group >> post_dbt



basic_eks_cosmos_task_group()
