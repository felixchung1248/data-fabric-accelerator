#!/bin/sh
set -euo pipefail

helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace -f value.yaml
