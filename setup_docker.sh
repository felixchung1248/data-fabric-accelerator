#!/bin/bash

ALIAS_NAME="kubectl"
ALIAS_COMMAND="/snap/bin/microk8s kubectl"
ALIAS_STRING="alias $ALIAS_NAME='$ALIAS_COMMAND'"
if grep -Fxq "$ALIAS_STRING" ~/.bashrc
then
    echo "Already install"
else
    echo "$ALIAS_STRING" >> ~/.bashrc
    echo "Installed kubectl"
fi
bash


# echo current user: $USER
# echo home path: $HOME

# SCRIPT_DIR=$(dirname "$0")

# # Change to that directory
# cd "$SCRIPT_DIR"

# # Add Docker's official GPG key:
# sudo apt-get update
# sudo apt-get install ca-certificates curl
# sudo install -m 0755 -d /etc/apt/keyrings
# sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
# sudo chmod a+r /etc/apt/keyrings/docker.asc

# # Add the repository to Apt sources:
# echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
#   $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
# sudo apt-get update

# # Install Docker
# VERSION_STRING=5:28.0.0-1~ubuntu.24.04~noble
# sudo apt-get install -y docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io docker-buildx-plugin docker-compose-plugin
