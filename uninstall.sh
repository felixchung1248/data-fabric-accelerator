#!/bin/bash
CONFIG_FILE="namespace.conf"

while IFS=',' read -r namespace path chart; do
  # Deploy the specified Helm chart to the namespace
  helm uninstall "$chart" -n "$namespace"
done < "$CONFIG_FILE"
