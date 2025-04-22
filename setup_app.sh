#!/bin/bash
CONFIG_FILE="namespace.conf"
DATAHUB_NAMESPACE=datahub-ns
TIMEOUT=15m0s

echo current user: $USER
echo home path: $HOME

SCRIPT_DIR=$(dirname "$0")

# Change to that directory
cd "$SCRIPT_DIR"

source setting.conf

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
kubectl get secret mysql-secrets -n $DATAHUB_NAMESPACE &> /dev/null || kubectl create secret generic mysql-secrets --from-literal=mysql-root-password='datahub' -n $DATAHUB_NAMESPACE
[ ! -z $OPENAI_KEY ] && kubectl create secret generic openai-secret --from-literal=openai-key=${OPENAI_KEY} --namespace=langchain-chatbot-denodo-ns

## Denodo Sandbox
[ ! -z $HARBOR_USR ] && [ ! -z $HARBOR_PW ] && kubectl create secret docker-registry harbor-registry-secret --docker-server=harbor.open.denodo.com --docker-username=${HARBOR_USR} --docker-password=${HARBOR_PW} -n denodo-sandbox-ns
[ ! -z $LICENSE_PATH ] && kubectl create secret generic denodo-platform-license --from-file=denodo.lic=${LICENSE_PATH} --namespace denodo-sandbox-ns

## Denodo Production
[ ! -z $HARBOR_USR ] && [ ! -z $HARBOR_PW ] && kubectl create secret docker-registry harbor-registry-secret --docker-server=harbor.open.denodo.com --docker-username=${HARBOR_USR} --docker-password=${HARBOR_PW} -n denodo-ns
[ ! -z $LICENSE_PATH ] && kubectl create secret generic denodo-platform-license --from-file=denodo.lic=${LICENSE_PATH} --namespace denodo-ns

[ ! -z $HARBOR_USR ] && [ ! -z $HARBOR_PW ] && sed -e "s/DENODO_USR_VAL/${HARBOR_USR}/" -e "s/DENODO_PW_VAL/${HARBOR_PW}/" ./demo/jenkins/values.template.yaml > ./demo/jenkins/values.yaml

[ ! -z $DOCKERHUB_USR ] && [ ! -z $DOCKERHUB_PW ] && kubectl create secret docker-registry docker-registry-secret --docker-server=docker.io --docker-username=${DOCKERHUB_USR} --docker-password=${DOCKERHUB_PW} -n data-mgmt-web-ns

[ ! -z $HOST_IP ] && sed -e "s/HOST_IP/${HOST_IP}/" ./demo/data-mgmt-portal-deploy/values.template.yaml > ./demo/data-mgmt-portal-deploy/values.yaml

# Second loop: Deploy Helm charts
while IFS=',' read -r namespace path chart; do
  # Deploy the specified Helm chart to the namespace
  helm install "$chart" "$path" -n "$namespace" --timeout $TIMEOUT
done < "$CONFIG_FILE"

