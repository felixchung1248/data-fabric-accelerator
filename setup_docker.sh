#!/bin/bash
shopt -s expand_aliases
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


echo current user: $USER
echo home path: $HOME

SCRIPT_DIR=$(dirname "$0")

# Change to that directory
cd "$SCRIPT_DIR"

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
bash

# Install Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
