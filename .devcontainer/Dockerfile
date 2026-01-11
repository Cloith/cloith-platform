# Use the official Microsoft Dev Container base (Ubuntu-based)
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 1. Install Basic Essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-venv \
    sshpass \
    curl \
    git \
    gnupg2 \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Ansible (via Pip for latest version)
RUN pip3 install --no-cache-dir ansible

# 3. Install Kubectl (Latest Stable)
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl \
    && rm kubectl

# 4. Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 5. Install Tailscale CLI (To manage your tailnet from inside)
RUN curl -fsSL https://tailscale.com/install.sh | sh

# 6. Install Bitwarden CLI to handle secrets
RUN curl -L "https://vault.bitwarden.com/download/?app=cli&platform=linux" -o bw.zip \
    && unzip bw.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/bw \
    && rm bw.zip

# Set the default shell to bash
ENV SHELL=/bin/bash