#!bin/bash

#update and install basic tools (as every script starts)
sudo apt update && sudo apt -y curl wget unzip

#create the minio user
sudo useradd -r minio-user -s /user/sbin/nologin

#create directories
sudo mkdir -p /usr/local/bin /usr/local/share/minio /etc/minio /var/minio
sudo chown -R minio-user:minio-user /var/minio

#downloading binary
wget -O minio https://dl.min.io/server/minio/release/linux-amd64/archive/minio.RELEASE.2024-05-10T01-41-38Z
chmod +x minio
sudo mv minio /usr/local/bin

#downloading the client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin


