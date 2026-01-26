# Use the official Microsoft Dev Container base
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Basic Essentials & Terraform Prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
    sshpass \
    curl \
    git \
    gnupg2 \
    unzip \
    netcat-openbsd \
    lsb-release \
    software-properties-common \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 1.1 Install Terraform CLI (Official HashiCorp Repo)
RUN curl -fsSL https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update && apt-get install -y terraform

# 2. Install Ansible (via Pip)
RUN pip3 install --no-cache-dir ansible

# 3. Install Kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# 4. Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 5. Install Tailscale CLI
RUN curl -fsSL https://tailscale.com/install.sh | sh

# 6. Install Bitwarden CLI
RUN curl -L "https://vault.bitwarden.com/download/?app=cli&platform=linux" -o bw.zip \
    && unzip bw.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/bw \
    && rm bw.zip

# 7. Use the Venv's Pip to install everything (Guarantees the CLI tools go here)
RUN pip install --no-cache-dir \
    questionary \
    rich \
    pexpect \
    requests 

# Set the default shell to bash
ENV SHELL=/bin/bash