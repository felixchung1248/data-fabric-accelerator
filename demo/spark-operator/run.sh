#!/bin/sh
set -euo pipefail

helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm upgrade --install spark-operator spark-operator/spark-operator --namespace spark-operator --create-namespace --set "spark.jobNamespaces={spark-operator}" --set webhook.enable=true
