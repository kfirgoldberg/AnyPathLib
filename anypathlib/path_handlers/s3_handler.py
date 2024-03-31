import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple, Optional, ClassVar
from urllib.parse import urlparse

import boto3 as boto3
import botocore
from tqdm import tqdm

from anypathlib.path_handlers.base_path_handler import BasePathHandler


class S3Handler(BasePathHandler):
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
    MAX_POOL_CONNECTIONS = 50
    # Create a boto3 S3 client
    s3_client: ClassVar[boto3.client] = boto3.client('s3', config=botocore.config.Config(
        max_pool_connections=MAX_POOL_CONNECTIONS))

    @classmethod
    def refresh_credentials(cls):
        if cls.AWS_ACCESS_KEY_ID is None:
            cls.AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', None)
            cls.s3_client = boto3.client('s3',
                                         config=botocore.config.Config(max_pool_connections=cls.MAX_POOL_CONNECTIONS))

    @classmethod
    def relative_path(cls, url: str) -> str:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        return f'{bucket}/{key}'

    @classmethod
    def is_dir(cls, url: str) -> bool:
        return cls.exists(url) and not cls.is_file(url)

    @classmethod
    def is_file(cls, url: str) -> bool:
        bucket_name, object_key = cls.get_bucket_and_key_from_uri(url)
        try:
            cls.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            return True  # If the head object doesn't raise an error, it's a file
        except (cls.s3_client.exceptions.NoSuchKey, cls.s3_client.exceptions.ClientError):
            return False  # If a NoSuchKey error is raised, it's not a file

    @classmethod
    def parent(cls, url: str) -> str:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        return cls.get_full_path(bucket=bucket, key=Path(key).parent.as_posix())

    @classmethod
    def stem(cls, url: str) -> str:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        return Path(key).stem

    @classmethod
    def name(cls, url: str) -> str:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        return Path(key).name

    @classmethod
    def exists(cls, url: str) -> bool:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        try:
            resp = cls.s3_client.list_objects(Bucket=bucket, Prefix=key, Delimiter='/', MaxKeys=1)
            return 'Contents' in resp or 'CommonPrefixes' in resp
        except cls.s3_client.exceptions.NoSuchKey:
            return False

    @classmethod
    def get_bucket_and_key_from_uri(cls, s3_uri: str) -> Tuple[str, str]:
        parsed_uri = urlparse(s3_uri)
        bucket = parsed_uri.netloc
        key = parsed_uri.path.lstrip('/')
        cls.refresh_credentials()
        return bucket, key

    @classmethod
    def get_full_path(cls, bucket: str, key: str) -> str:

        return f's3://{bucket}/{key}'

    @classmethod
    def download_file(cls, url: str, target_path: Path, force_overwrite: bool = True) -> Path:
        # Convert the local path to a Path object
        local_file_path = Path(target_path)
        if not force_overwrite and local_file_path.exists():
            return local_file_path
        # Parse the S3 URL
        bucket, key = cls.get_bucket_and_key_from_uri(url)

        # Ensure the local directory exists
        local_file_path.parent.mkdir(parents=True, exist_ok=True)
        # Download the file
        cls.s3_client.download_file(Bucket=bucket, Key=key, Filename=local_file_path.absolute().as_posix())
        return local_file_path

    @classmethod
    def listdir(cls, url: str) -> List[str]:
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucket)
        items = [cls.get_full_path(bucket=bucket.name, key=obj.key) for obj in bucket.objects.filter(Prefix=key)]
        items = [item for item in items if item != url]
        return items

    @classmethod
    def remove(cls, url: str):
        bucket, key = cls.get_bucket_and_key_from_uri(url)
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(bucket)
        bucket.objects.filter(Prefix=key).delete()

    @classmethod
    def download_directory(cls, url: str, force_overwrite: bool, target_dir: Path) -> \
            Optional[Tuple[Path, List[Path]]]:

        s3_resource = boto3.resource('s3')

        bucket, source_key = cls.get_bucket_and_key_from_uri(url)
        bucket = s3_resource.Bucket(bucket)
        all_files = []

        # Prepare the list of s3_paths to download
        s3_paths: List[str] = [cls.get_full_path(bucket=bucket.name, key=obj.key) for obj in
                               bucket.objects.filter(Prefix=source_key)]
        s3_paths = [s3_path for s3_path in s3_paths if s3_path.rstrip('/') != url]

        def s3_path_to_local_file_path(s3_path: str, local_base_path: Path) -> Path:
            _, key = cls.get_bucket_and_key_from_uri(s3_path)
            local_file_relative_path = Path(key).relative_to(source_key)
            return local_base_path / local_file_relative_path

        # Download in parallel
        with ThreadPoolExecutor() as executor:
            future_to_s3_path = {executor.submit(cls.download_file,
                                                 url=s3_path,
                                                 target_path=s3_path_to_local_file_path(s3_path=s3_path,
                                                                                        local_base_path=target_dir),
                                                 force_overwrite=force_overwrite): s3_path for s3_path in s3_paths}

            with tqdm(total=len(s3_paths), desc='Downloading directory') as pbar:
                for future in as_completed(future_to_s3_path):
                    s3_path = future_to_s3_path[future]
                    try:
                        local_path = future.result()
                        if local_path:
                            all_files.append(local_path)
                    except Exception as exc:
                        print(f'{s3_path} generated an exception: {exc}')

                    pbar.update(1)

        return target_dir, all_files

    @classmethod
    def upload_file(cls, local_path: str, target_url: str):
        bucket, key = cls.get_bucket_and_key_from_uri(target_url)
        cls.s3_client.upload_file(local_path, bucket, key)

    @classmethod
    def upload_directory(cls, local_dir: Path, target_url: str):
        bucket, key = cls.get_bucket_and_key_from_uri(target_url)
        for root, dirs, files in tqdm(os.walk(local_dir), desc='Uploading directory'):
            for file in files:
                local_path = os.path.join(root, file)
                s3_key = f'{key}/{os.path.relpath(local_path, local_dir)}'
                cls.s3_client.upload_file(local_path, bucket, s3_key)

    @classmethod
    def copy(cls, source_url: str, target_url: str):
        s3_resource = boto3.resource('s3')
        source_bucket_name, source_key = cls.get_bucket_and_key_from_uri(source_url)
        target_bucket_name, target_key = cls.get_bucket_and_key_from_uri(target_url)

        source_bucket = s3_resource.Bucket(source_bucket_name)
        objects = list(source_bucket.objects.filter(Prefix=source_key))

        def copy_and_delete(obj):
            new_key = obj.key.replace(source_key, target_key, 1)
            copy_source = {
                'Bucket': source_bucket_name,
                'Key': obj.key
            }
            # Copy object to the new location
            s3_resource.meta.client.copy(copy_source, target_bucket_name, new_key)

        # Use ThreadPoolExecutor to parallelize the operation
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(copy_and_delete, obj) for obj in objects]

            for future in as_completed(futures):
                try:
                    future.result()  # If needed, handle result or exceptions here
                except Exception as exc:
                    print(f'Operation generated an exception: {exc}')
