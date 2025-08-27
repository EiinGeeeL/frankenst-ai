import os
import tempfile
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from core.utils.key_vault import get_secret

def upload_file_to_blob(blob_path: str, content: str, container_name: str):
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("La variable de entorno 'AzureWebJobsStorage' no está configurada")

    # Crear cliente del servicio Blob
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Crear el contenedor si no existe
    try:
        blob_service_client.create_container(container_name)
    except ResourceExistsError:
        pass

    # Subir contenido directamente
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
    blob_client.upload_blob(content, overwrite=True)

    return f"Archivo '{blob_path}' cargado correctamente en el contenedor '{container_name}'."

def load_text_from_blob(blob_path: str, container_name: str) -> str:
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("La variable de entorno 'AzureWebJobsStorage' no está configurada")

    # Crear cliente del servicio Blob
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Obtener el cliente del blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    try:
        # Descargar el contenido del blob
        download_stream = blob_client.download_blob()
        content = download_stream.readall().decode("utf-8")  # Asumimos que el contenido es texto
        return content

    except ResourceNotFoundError:
        raise FileNotFoundError(f"No se encontró el blob '{blob_path}' en el contenedor '{container_name}'")

def download_pdf_from_blob(blob_path: str, container_name: str) -> str:
    """
    Descarga un archivo PDF desde Azure Blob Storage y lo guarda en un archivo temporal local.
    Retorna la ruta del archivo temporal.
    """
    connection_string = get_secret('AzureWebJobsStorage')
    if not connection_string:
        raise ValueError("La variable de entorno 'AzureWebJobsStorage' no está configurada")

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
        raise FileNotFoundError(f"No se encontró el blob '{blob_path}' en el contenedor '{container_name}'")


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
