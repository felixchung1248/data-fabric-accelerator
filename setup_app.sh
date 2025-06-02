#!/bin/bash
CONFIG_FILE="namespace.conf"
DATAHUB_NAMESPACE=datahub-ns
MCP_AGENTIC_DREMIO_NAMESPACE=mcp-agentic-dremio-ns
TIMEOUT=15m0s

echo current user: $USER
echo home path: $HOME

SCRIPT_DIR=$(dirname "$0")
cd "$SCRIPT_DIR"

# First loop: Create all namespaces
declare -A namespace_created
while IFS=',' read -r namespace path chart; do
  # Check if the namespace has already been processed
  if [ -z "${namespace_created[$namespace]}" ]; then
    kubectl get namespace "$namespace" &> /dev/null || kubectl create namespace "$namespace"
    namespace_created[$namespace]=1
  fi
done < "$CONFIG_FILE"

# Create required secrets
kubectl get namespace $DATAHUB_NAMESPACE &> /dev/null && kubectl get secret mysql-secrets -n $DATAHUB_NAMESPACE &> /dev/null || kubectl create secret generic mysql-secrets --from-literal=mysql-root-password='datahub' -n $DATAHUB_NAMESPACE
[ ! -z $API_KEY ] && kubectl get namespace $MCP_AGENTIC_DREMIO_NAMESPACE &> /dev/null && kubectl get secret api-key -n $MCP_AGENTIC_DREMIO_NAMESPACE &> /dev/null || kubectl create secret generic api-key --from-literal=api-key=${API_KEY} -n $MCP_AGENTIC_DREMIO_NAMESPACE

[ ! -z $HOST_IP ] && sed -e "s/HOST_IP/${HOST_IP}/" ./demo/data-mgmt-portal-deploy/values.template.yaml > ./demo/data-mgmt-portal-deploy/values.yaml

# Second loop: Deploy Helm charts
while IFS=',' read -r namespace path chart; do
  # Deploy the specified Helm chart to the namespace
  helm install "$chart" "$path" -n "$namespace" --timeout $TIMEOUT
done < "$CONFIG_FILE"

