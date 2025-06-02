# Centralized data management platform sample

## Introduction
This repository allows you to quickly spin up a data management platform made with a number of open source applications in your own environment. It aims at giving you an idea of what a modernized data management looks like. Feel free to comment if you have any thought!

## Background
As you know, a modernized data management is not only IT-managed, but also a more complex and multi-dimensional data teams with the support of well-defined operating model. Decentralized data analytics (or the so-called "data-as-a-product", or "self-service") is more common in the market. This repository aims at giving you some ideas how the data platform can look like to facilitate this "self-service" operating model. For more details of the operating model, please check my below Medium article
[Medium article](https://medium.com/data-openness-community/4-actions-to-shorten-data-engineering-delivery-time-922dbab862f2)

![Alt Text](https://miro.medium.com/v2/resize:fit:1100/format:webp/1*kylvy2d5e_G5kxoAGUnqqA.gif)

## Features

### Data Marketplace ###
- Self-service dataset deployment from sandbox to production with governance
- GenAI chatbot to query internal data 

## Prerequisite
1. Prepare a machine running in Ubuntu with Internet access. (Mine was Ubuntu 24 with 8vcpu / 32g memory in Azure Southeast Asia when I developed this platform). I recommend a new and clean machine to avoid any issue
2. Download this repository into your machine
3. (Optional) Run the below setup scripts as below to install Docker if your machine doesn't have it
```bash
chmod +x data-fabric-accelerator/setup*.sh
./data-fabric-accelerator/setup_docker.sh ## can skip if the machine has installed docker
```
4a. (Optional) Run the below setup scripts as below to install K8s if your machine doesn't have it
```bash
./data-fabric-accelerator/setup_k8s.sh ## can skip if the machine has installed K8s
```
4b. (Optional) Re-login your machine. Run the below commands to enable K8s ingress, dns and dashboard
```bash
microk8s enable dashboard dns ingress
microk8s start
microk8s enable hostpath-storage
microk8s config > $HOME/.kube/config
microk8s dashboard-proxy
```

5. (Optional) Run the below setup scripts as below to install Helm if your machine doesn't have it
```bash
./data-fabric-accelerator/setup_helm.sh ## can skip if the machine has installed Helm
```

6a. (Optional) Go to openrouter.ai, register an account for some free GenAI models and create an API key

6b. (Optional) Export API_KEY to use Agentic AI feature for data analytics
```bash
export API_KEY={your API key from openrouter.ai} ## can skip if the machine has installed Helm
```

## Installation
1. Re-login your machine. Run the below to install all application components for the data fabric platform
```bash
chmod +x data-fabric-accelerator/setup*.sh
./data-fabric-accelerator/setup_app.sh
```

### Accesssing the Kubenetes Dashboard
1. If 6b has been performed, the dashboard should have been enabled.
2. Open a new session of your machine
3. Run `microk8s kubectl port-forward -n kube-system service/kubernetes-dashboard 10443:443`
4. Access the Kubernetes Dashboard on `<Your VM IP>`:10443




## Links for core components

| Application | URL    | Description |
| :-------- | :------- | :------- |
| Data management portal | http://`<Your VM IP>`:30030 | Centralized portal for necessary data activities, e.g. dataset deployment, GenAI chatbot |
| Dremio Production | http://`<Your VM IP>`:30047 | Core data platform for data users to perform testing |
| DataHub | http://`<Your VM IP>`:31002  | Data Catalog and data lineage |
| Zammad | http://`<Your VM IP>`:30880  | ITSM (not necessary for data platform but to provide end-to-end governed data workflow) |
| Jenkins | http://`<Your VM IP>`:30808  | CD pipeline for dataset deployment |
| MinIO | http://`<Your VM IP>`:31090  | Object storage for user drop zone |


## Links for optional components
| Application | URL    | Description |
| :-------- | :------- | :------- |
| pgadmin4 | http://`<Your VM IP>`:30080 | Workbench for postgres data source operations, e.g. create table to test and illustrate Denodo's data virtualization |
| K8s dashboard | https://`<Your VM IP>`:10043 | K8s access for troubleshooting |