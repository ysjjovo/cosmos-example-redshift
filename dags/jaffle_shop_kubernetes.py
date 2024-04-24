"""
## Jaffle Shop DAG
[Jaffle Shop](https://github.com/dbt-labs/jaffle_shop) is a fictional eCommerce store. This dbt project originates from
dbt labs as an example project with dummy data to demonstrate a working dbt core project. This DAG uses the cosmos dbt
parser to generate an Airflow TaskGroup from the dbt project folder.


The step-by-step to run this DAG are described in:
https://astronomer.github.io/astronomer-cosmos/getting_started/kubernetes.html#kubernetes

"""
from pathlib import Path

from airflow import DAG
# from airflow.providers.cncf.kubernetes.secret import Secret
from pendulum import datetime

from cosmos import (
    ProjectConfig,
    ProfileConfig,
    ExecutionConfig,
    ExecutionMode,
    # DbtSeedKubernetesOperator,
    DbtTaskGroup,
)
from cosmos.profiles import RedshiftUserPasswordProfileMapping
from airflow.operators.empty import EmptyOperator

PROJECT_DIR = Path("dags/dbt/jaffle_shop/")
DBT_IMAGE = "139260835254.dkr.ecr.us-east-2.amazonaws.com/dbt-jaffle-shop:1.0.0"

project_seeds = [
    {"project": "jaffle_shop", "seeds": ["raw_customers", "raw_payments", "raw_orders"]}
]

with DAG(
    dag_id="jaffle_shop_kubernetes_redshift",
    start_date=datetime(2022, 11, 27),
    doc_md=__doc__,
    catchup=False,
) as dag:
    # load_seeds = DbtSeedKubernetesOperator(
    #     task_id="load_seeds",
    #     project_dir=PROJECT_DIR,
    #     get_logs=True,
    #     schema="public",
    #     conn_id="postgres_default",
    #     image=DBT_IMAGE,
    #     is_delete_operator_pod=False,
    #     secrets=[postgres_password_secret, postgres_host_secret],
    # )

    run_models = DbtTaskGroup(
        profile_config=ProfileConfig(
            profile_name="redshift_profile",
            target_name="dev",
            profile_mapping=RedshiftUserPasswordProfileMapping(
                conn_id="redshift_default",
                profile_args={
                    "schema": "public",
                },
            ),
        ),
        project_config=ProjectConfig(PROJECT_DIR),
        execution_config=ExecutionConfig(
            execution_mode=ExecutionMode.KUBERNETES,
        ),
        operator_args={
            "image": DBT_IMAGE,
            "get_logs": True,
            "is_delete_operator_pod": False,
             "env_vars": {"TARGT": "prod_password",
                         "HOST": '', 
                         "PORT": '',
                         "USER": '',
                         "PASSWORD": '',
                         "DATABASE": '',
                         "SCHEMA": '',
                        },
        },
    )
    e1 = EmptyOperator(task_id="pre_dbt")
    e2 = EmptyOperator(task_id="post_dbt")
    e1 >> run_models >> e2
