import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import urlparse

from azure.core.exceptions import ResourceNotFoundError

from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient

from loguru import logger

from anypathlib.path_handlers.base_path_handler import BasePathHandler


@dataclass
class AzureStoragePath:
    storage_account: str
    container_name: str
    blob_name: str
    connection_string: Optional[str] = None

    def __post_init__(self):
        if self.connection_string is None:
            self.connection_string = AzureHandler.get_connection_string(self.storage_account)

    @property
    def http_url(self) -> str:
        return f'https://{self.storage_account}.blob.core.windows.net/{self.container_name}/{self.blob_name}'


class AzureHandler(BasePathHandler):
    DEFAULT_SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID', None)

    DEFAULT_GROUP_NAME = os.environ.get('AZURE_RESOURCE_GROUP_NAME', None)

    @classmethod
    def refresh_credentials(cls):
        if cls.DEFAULT_SUBSCRIPTION_ID is None:
            cls.DEFAULT_SUBSCRIPTION_ID = os.environ.get('AZURE_SUBSCRIPTION_ID', None)
        if cls.DEFAULT_GROUP_NAME is None:
            cls.DEFAULT_GROUP_NAME = os.environ.get('AZURE_RESOURCE_GROUP_NAME', None)

    @classmethod
    def relative_path(cls, url: str) -> str:
        storage_path = cls.http_to_storage_params(url)
        return f'{storage_path.container_name}/{storage_path.blob_name}'

    @classmethod
    def is_dir(cls, url: str) -> bool:
        return cls.exists(url) and not cls.is_file(url)

    @classmethod
    def is_file(cls, url: str) -> bool:
        storage_path = cls.http_to_storage_params(url)
        blob_service_client = BlobServiceClient(
            account_url=f"https://{storage_path.storage_account}.blob.core.windows.net")
        container_client = blob_service_client.get_container_client(storage_path.container_name)
        blob_client = container_client.get_blob_client(storage_path.blob_name)

        try:
            blob_properties = blob_client.get_blob_properties()
            # If the blob exists and is not a directory placeholder, it's a file
            return not blob_properties.metadata.get('hdi_isfolder', False)
        except Exception:
            return False  # If exception is raised, the blob does not exist or is not a file

    @classmethod
    def exists(cls, url: str) -> bool:
        storage_path = cls.http_to_storage_params(url)

        blob_service_client = BlobServiceClient.from_connection_string(storage_path.connection_string)
        container_client = blob_service_client.get_container_client(container=storage_path.container_name)
        return len([p for p in container_client.list_blobs(name_starts_with=storage_path.blob_name)]) > 0

    @classmethod
    def get_connection_string(cls, storage_account: str, subscription_id: Optional[str] = None,
                              resource_group_name: Optional[str] = None) -> str:
        cls.refresh_credentials()
        account_key = cls.get_storage_account_key(storage_account_name=storage_account, subscription_id=subscription_id,
                                                  resource_group_name=resource_group_name)
        connection_string = (f"DefaultEndpointsProtocol=https;AccountName={storage_account};"
                             f"AccountKey={account_key};EndpointSuffix=core.windows.net")
        return connection_string

    @classmethod
    def http_to_storage_params(cls, url: str) -> AzureStoragePath:
        parsed_url = urlparse(url)
        account_name = parsed_url.netloc.split('.')[0]
        container_name, *blob_path_parts = parsed_url.path.lstrip('/').split('/')
        blob_path = '/'.join(blob_path_parts)

        azure_storage_path = AzureStoragePath(storage_account=account_name, container_name=container_name,
                                              blob_name=blob_path)
        return azure_storage_path

    @classmethod
    def get_storage_account_key(cls,
                                storage_account_name: str,
                                subscription_id: Optional[str] = None,
                                resource_group_name: Optional[str] = None,
                                ) -> str:
        """
        Retrieves the access key for a storage account in Azure.

        Args:
            subscription_id (str): The subscription ID of the Azure account.
            resource_group_name (str): The name of the resource group containing the storage account.
            storage_account_name (str): The name of the storage account.

        Returns:
            str: The access key for the storage account.
        """
        try:
            if subscription_id is None:
                subscription_id = cls.DEFAULT_SUBSCRIPTION_ID
                if subscription_id is None:
                    raise ValueError(
                        """
                        No subscription ID was provided.
                        Set the AZURE_SUBSCRIPTION_ID environment variable, or pass it as an argument.
                        """
                    )
            if resource_group_name is None:
                resource_group_name = cls.DEFAULT_GROUP_NAME
                if resource_group_name is None:
                    raise ValueError(
                        """
                        No resource group name was provided.
                        Set the AZURE_RESOURCE_GROUP_NAME environment variable, or pass it as an argument.
                        """
                    )
            client = StorageManagementClient(credential=DefaultAzureCredential(), subscription_id=subscription_id)
            response = client.storage_accounts.list_keys(resource_group_name=resource_group_name,
                                                         account_name=storage_account_name, )
            if not response.keys:
                raise ValueError(
                    """
                    No keys were found for the storage account.
                    Ask the MLOps guys for the access key, or try and get it from the Azure portal
                    """
                )
            return response.keys[0].value  # Returns the first key of the storage account
        except Exception as e:
            logger.exception(e)
            logger.exception(
                """
                There was an error fetching the storage account key.
                Make sure you are connected to VPN, and config is correct.
                If it still fails, get it from the Azure portal,
                or ask the MLOps guys for the access key.
                """
            )
            raise e

    @classmethod
    def download_file(cls, url: str, target_path: Path, force_overwrite: bool = True) -> Path:
        if target_path.exists() and not force_overwrite:
            return target_path
        azure_storage_path = cls.http_to_storage_params(url)
        # Construct the Blob Service Client
        blob_service_client = BlobServiceClient(
            account_url=f"https://{azure_storage_path.storage_account}.blob.core.windows.net")

        # Get a client to interact with the specified container and blob
        blob_client = blob_service_client.get_blob_client(container=azure_storage_path.container_name,
                                                          blob=azure_storage_path.blob_name)

        # Ensure the directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Download the blob to a local file
        with open(target_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        return target_path

    @classmethod
    def upload_file(cls, local_path: str, target_url: str):
        azure_storage_path = cls.http_to_storage_params(target_url)
        """Upload a single file to Azure Blob Storage."""
        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)

        # Check if the container exists and create if it does not
        container_client = blob_service_client.get_container_client(azure_storage_path.container_name)
        try:
            container_client.get_container_properties()
        except Exception as e:
            # Assuming exception means container does not exist. Create new container
            container_client.create_container()

        # Now, upload the file
        blob_client = blob_service_client.get_blob_client(container=azure_storage_path.container_name,
                                                          blob=azure_storage_path.blob_name)
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

    @classmethod
    def listdir(cls, url: str, with_prefix: bool = True) -> List[str]:
        """List a directory (all blobs with the same prefix) from Azure Blob Storage."""
        azure_storage_path = cls.http_to_storage_params(url)
        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)
        container_client = blob_service_client.get_container_client(container=azure_storage_path.container_name)
        blob_names = []
        for blob in container_client.list_blobs(name_starts_with=azure_storage_path.blob_name):
            blob_name = blob.name if with_prefix else blob.name.replace(azure_storage_path.blob_name, '')
            blob_azure_path = AzureStoragePath(storage_account=azure_storage_path.storage_account,
                                               container_name=azure_storage_path.container_name, blob_name=blob_name,
                                               connection_string=azure_storage_path.connection_string)
            blob_names.append(blob_azure_path.http_url)
        items = [item for item in blob_names if item != url]
        return items

    @classmethod
    def remove_directory(cls, url: str):
        """Remove a directory (all blobs with the same prefix) from Azure Blob Storage."""
        azure_storage_path = cls.http_to_storage_params(url)
        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)
        container_client = blob_service_client.get_container_client(container=azure_storage_path.container_name)
        for blob in container_client.list_blobs(name_starts_with=azure_storage_path.blob_name):
            container_client.delete_blob(blob.name)

    @classmethod
    def remove(cls, url: str, allow_missing: bool = False):
        """Remove a single file/directory from Azure Blob Storage."""
        if url.endswith('/'):
            cls.remove_directory(url)
        else:
            azure_storage_path = cls.http_to_storage_params(url)
            blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)
            container_client = blob_service_client.get_container_client(container=azure_storage_path.container_name)
            try:
                container_client.delete_blob(azure_storage_path.blob_name)
            except ResourceNotFoundError as e:
                if not allow_missing:
                    raise e

    @classmethod
    def download_directory(cls, url: str, force_overwrite: bool, target_dir: Path) -> \
            Optional[Tuple[Path, List[Path]]]:
        """Download a directory (all blobs with the same prefix) from Azure Blob Storage."""
        assert target_dir.is_dir()
        azure_storage_path = cls.http_to_storage_params(url)

        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)
        container_client = blob_service_client.get_container_client(container=azure_storage_path.container_name)
        local_paths = []
        blob_urls = []
        for blob in container_client.list_blobs(name_starts_with=azure_storage_path.blob_name):
            blob_url = AzureStoragePath(storage_account=azure_storage_path.storage_account,
                                        container_name=azure_storage_path.container_name, blob_name=blob.name,
                                        connection_string=azure_storage_path.connection_string).http_url
            local_target = target_dir / blob.name
            local_path = cls.download_file(url=blob_url, force_overwrite=force_overwrite, target_path=local_target)
            assert local_path is not None, f'could not download from {url}'
            local_paths.append(Path(local_path))
            blob_urls.append(blob_url)
        if len(local_paths) == 0:
            return None
        if target_dir is not None:
            local_files = []
            for blob_url, local_file in zip(blob_urls, local_paths):
                relative_path = Path(blob_url).relative_to(Path(url))
                target_path = target_dir / relative_path
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(local_file, target_path)
                local_files.append(target_path)
            return target_dir, local_files
        return local_paths[0].parent, local_paths

    @classmethod
    def upload_directory(cls, local_dir: Path, target_url: str):
        """Upload a directory to Azure Blob Storage."""
        azure_storage_path = cls.http_to_storage_params(target_url)
        blob_service_client = BlobServiceClient.from_connection_string(azure_storage_path.connection_string)
        # Check if the container exists and create if it does not
        container_client = blob_service_client.get_container_client(azure_storage_path.container_name)
        try:
            container_client.get_container_properties()
        except Exception as e:
            # Assuming exception means container does not exist. Create new container
            container_client.create_container()

        def upload_file_wrapper(local_path: str, blob_name: str):
            azure_url = rf'azure://{azure_storage_path.storage_account}/{azure_storage_path.container_name}/{blob_name}'
            cls.upload_file(local_path=local_path, target_url=azure_url)

        # Collect all files to upload
        files_to_upload = []
        # for file_path in local_dir.iterdir():
        for file_path in local_dir.rglob('*'):
            if not file_path.is_file():
                continue
            blob_name = os.path.join(azure_storage_path.blob_name, file_path.relative_to(local_dir))
            files_to_upload.append((file_path, blob_name))

        # Upload files in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(upload_file_wrapper, str(local_path), blob_name) for local_path, blob_name in
                       files_to_upload]
            for future in futures:
                future.result()  # Wait for each upload to complete

    @classmethod
    def copy(cls, source_url: str, target_url: str):
        source_storage_path = cls.http_to_storage_params(source_url)
        target_storage_path = cls.http_to_storage_params(target_url)

        source_blob_service_client = BlobServiceClient.from_connection_string(
            source_storage_path.connection_string)
        target_blob_service_client = BlobServiceClient.from_connection_string(
            target_storage_path.connection_string)

        source_container_client = source_blob_service_client.get_container_client(
            source_storage_path.container_name)

        blobs_to_rename = source_container_client.list_blobs(name_starts_with=source_storage_path.blob_name)

        def copy_blob(blob):
            source_blob_url = AzureStoragePath(storage_account=source_storage_path.storage_account,
                                               container_name=source_storage_path.container_name, blob_name=blob.name,
                                               connection_string=source_storage_path.connection_string).http_url
            target_blob_name = blob.name.replace(source_storage_path.blob_name, target_storage_path.blob_name, 1)

            # Copy to new location
            target_blob = target_blob_service_client.get_blob_client(container=target_storage_path.container_name,
                                                                     blob=target_blob_name)
            target_blob.start_copy_from_url(source_blob_url)

        # Execute copy and delete operations in parallel
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(copy_blob, blob) for blob in blobs_to_rename]
            for future in futures:
                future.result()  # Wait for each operation to complete

    @classmethod
    def parent(cls, url: str) -> str:
        parsed_url = urlparse(url)
        account_name = parsed_url.netloc.split('.')[0]
        container_name, *blob_path_parts = parsed_url.path.lstrip('/').split('/')
        if blob_path_parts[-1] == "":
            blob_path_parts = blob_path_parts[:-1]
        blob_path = '/'.join(blob_path_parts[:-1])
        parent_url = f'https://{account_name}.blob.core.windows.net/{container_name}/{blob_path}/'
        return parent_url

    @classmethod
    def name(cls, url: str) -> str:
        parsed_url = urlparse(url)
        container_name, *blob_path_parts = parsed_url.path.lstrip('/').split('/')
        if blob_path_parts[-1] == "":
            blob_path_parts = blob_path_parts[:-1]
        blob_name = blob_path_parts[-1]
        return blob_name

    @classmethod
    def stem(cls, url: str) -> str:
        parsed_url = urlparse(url)
        container_name, *blob_path_parts = parsed_url.path.lstrip('/').split('/')
        if blob_path_parts[-1] == "":
            blob_path_parts = blob_path_parts[:-1]
        blob_name = blob_path_parts[-1]
        return Path(blob_name).stem
