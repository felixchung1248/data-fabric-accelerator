#!/bin/bash
shopt -s expand_aliases
BASHRC_FILE="$HOME/.bash_aliases"

ALIAS_NAME="helm"
ALIAS_COMMAND="/snap/bin/microk8s $ALIAS_NAME"
ALIAS_STRING="alias $ALIAS_NAME='$ALIAS_COMMAND'"
if [ -f "$BASHRC_FILE" ] && grep -Fxq "$ALIAS_STRING" "$BASHRC_FILE"; then
    echo "Already installed"
else
    echo "$ALIAS_STRING" >> "$BASHRC_FILE"
    echo "Installed $ALIAS_NAME"
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




