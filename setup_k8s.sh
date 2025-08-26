#!/bin/bash
shopt -s expand_aliases

echo current user: $USER
echo home path: $HOME

SCRIPT_DIR=$(dirname "$0")

# Change to that directory
cd "$SCRIPT_DIR"


# Install K8s
sudo snap install microk8s --classic
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
#newgrp microk8s

#curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
#sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
BASHRC_FILE="$HOME/.bash_aliases"

ALIAS_NAME="kubectl"
ALIAS_COMMAND="/snap/bin/microk8s $ALIAS_NAME"
ALIAS_STRING="alias $ALIAS_NAME='$ALIAS_COMMAND'"
if [ -f "$BASHRC_FILE" ] && grep -Fxq "$ALIAS_STRING" "$BASHRC_FILE"; then
    echo "Already installed"
else
    echo "$ALIAS_STRING" >> "$BASHRC_FILE"
    echo "Installed $ALIAS_NAME"
fi



