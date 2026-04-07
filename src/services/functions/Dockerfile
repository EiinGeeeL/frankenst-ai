FROM mcr.microsoft.com/azure-functions/python:4-python3.12

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Define build arguments and set environment variables
ARG AZURE_KEY_VAULT_NAME

ENV AZURE_KEY_VAULT_NAME=${AZURE_KEY_VAULT_NAME}

# Install system dependencies and uv
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        unixodbc \
        curl \
        ca-certificates && \
    curl -fsSL https://astral.sh/uv/install.sh | sh && \
    apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*
ENV PATH="/home/.local/bin:$PATH"

# Install Python requirements
COPY requirements*.txt /tmp/requirements/
RUN uv pip install --system -r /tmp/requirements/requirements.txt \
    && rm -rf /tmp/requirements


# Prepare Function App
COPY . /home/site/wwwroot

# Move src modules and Function App core to the wwwroot and clean up
RUN mv /home/site/wwwroot/src/services/functions/* /home/site/wwwroot/ && \
    mv /home/site/wwwroot/src/* /home/site/wwwroot/ && \
    rm -rf /home/site/wwwroot/src