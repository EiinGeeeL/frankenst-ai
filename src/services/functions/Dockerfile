FROM mcr.microsoft.com/azure-functions/python:4-python3.12

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -y \
    unixodbc \
    && apt-get clean

# Define build arguments
ARG AZURE_KEY_VAULT_NAME
ARG TIMER_SCHEDULE

# Set environment variables
ENV AZURE_KEY_VAULT_NAME=$AZURE_KEY_VAULT_NAME \
    TIMER_SCHEDULE=$TIMER_SCHEDULE

# Install requirements
COPY requirements.txt /
RUN pip install -r requirements.txt

# Copy the entire project
COPY . /home/site/wwwroot

# Move the src modules and the functions app core to the wwwroot and clean up
RUN mv /home/site/wwwroot/src/services/functions/* /home/site/wwwroot/ && \
    mv /home/site/wwwroot/src/* /home/site/wwwroot/ && \
    rm -rf /home/site/wwwroot/src