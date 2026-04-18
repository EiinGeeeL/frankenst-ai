import os
import tempfile
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from core_examples.utils.key_vault import get_secret

def upload_file_to_blob(blob_path: str, content: str, container_name: str):
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("The 'AzureWebJobsStorage' secret is not configured")

    # Create the blob service client.
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Create the container when it does not exist yet.
    try:
        blob_service_client.create_container(container_name)
    except ResourceExistsError:
        pass

    # Upload the content directly.
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
    blob_client.upload_blob(content, overwrite=True)

    return f"File '{blob_path}' uploaded successfully to container '{container_name}'."

def load_text_from_blob(blob_path: str, container_name: str) -> str:
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("The 'AzureWebJobsStorage' secret is not configured")

    # Create the blob service client.
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get the blob client.
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    try:
        # Download the blob content.
        download_stream = blob_client.download_blob()
        content = download_stream.readall().decode("utf-8")
        return content

    except ResourceNotFoundError:
        raise FileNotFoundError(
            f"Blob '{blob_path}' was not found in container '{container_name}'"
        )

def download_pdf_from_blob(blob_path: str, container_name: str) -> str:
    """Download a PDF from Azure Blob Storage into a local temporary file."""
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("The 'AzureWebJobsStorage' secret is not configured")

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    try:
        filename = os.path.basename(blob_path)
        download_stream = blob_client.download_blob()

        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)

        with open(temp_path, "wb") as temp_file:
            temp_file.write(download_stream.readall())

        return temp_path
    
    except ResourceNotFoundError:
        raise FileNotFoundError(
            f"Blob '{blob_path}' was not found in container '{container_name}'"
        )


def parse_blob_subject(subject: str):
    """
    Parses a blob subject string with the structure:
    /blobServices/default/containers/{container_name}/blobs/{blob_path}

    Returns:
        tuple: (blob_path: str, container_name: str)
    """
    parts = subject.strip("/").split("/")

    try:
        container_index = parts.index("containers") + 1
        blobs_index = parts.index("blobs") + 1
    except ValueError:
        raise ValueError("Invalid subject format: missing 'containers' or 'blobs' segment")

    container_name = parts[container_index]
    blob_parts = parts[blobs_index:]

    if not blob_parts:
        raise ValueError("Invalid subject format: blob path is missing")

    blob_path = "/".join(blob_parts)
    return blob_path, container_name
