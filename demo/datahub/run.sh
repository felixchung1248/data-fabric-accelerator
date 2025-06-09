#!/bin/sh
set -euo pipefail

helm repo add datahub https://helm.datahubproject.io
helm install datahub datahub/datahub --namespace datahub-ns --create-namespace --version 0.4.19 --values value.yaml
