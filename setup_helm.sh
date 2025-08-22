#!/bin/bash

ALIAS_NAME="helm"
ALIAS_COMMAND="/snap/bin/microk8s helm"
ALIAS_STRING="alias $ALIAS_NAME='$ALIAS_COMMAND'"
if grep -Fxq "$ALIAS_STRING" ~/.bashrc
then
    echo "Already install"
else
    echo "$ALIAS_STRING" >> ~/.bashrc
    echo "Installed helm"
fi
bash

# echo current user: $USER
# echo home path: $HOME

# SCRIPT_DIR=$(dirname "$0")

# # Change to that directory
# cd "$SCRIPT_DIR"

# # Install Helm
# curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
# chmod 700 get_helm.sh
# ./get_helm.sh




