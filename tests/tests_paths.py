import os

from anypathlib import PathType
from anypathlib.path_handlers.azure_handler import AzureHandler
from anypathlib.path_handlers.local_handler import LocalPathHandler
from anypathlib.path_handlers.s3_handler import S3Handler

PATH_TYPE_TO_BASE_TEST_PATH = {PathType.s3: os.environ['ANYPATH_S3_TEST_URL'],
                               PathType.azure: os.environ['ANYPATH_AZURE_TEST_URL'],
                               PathType.local: os.environ['ANYPATH_LOCAL_TEST_URL']}
PATH_TYPE_TO_HANDLER = {PathType.s3: S3Handler, PathType.azure: AzureHandler, PathType.local: LocalPathHandler}
