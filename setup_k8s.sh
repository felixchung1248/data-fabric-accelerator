#!/bin/bash

echo current user: $USER
echo home path: $HOME

SCRIPT_DIR=$(dirname "$0")

# Change to that directory
cd "$SCRIPT_DIR"


# Install K8s
sudo snap install microk8s --classic
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl




