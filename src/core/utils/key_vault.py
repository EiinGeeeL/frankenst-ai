import os
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret(secret_name: str) -> str:
    # First, check if the secret is available as an environment variable
    if secret_value := os.getenv(secret_name):
        return secret_value

    # Get Key Vault name from environment variable
    key_vault_name = os.getenv("AZURE_KEY_VAULT_NAME")
    if not key_vault_name:
        raise Exception("AZURE_KEY_VAULT_NAME environment variable is not set")

    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_uri, credential=credential)
    
    try:
        secret = client.get_secret(secret_name)
        return secret.value
    except Exception as e:
        raise Exception(f"Error retrieving secret '{secret_name}': {str(e)}")
