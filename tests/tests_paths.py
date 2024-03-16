from anypathlib import PathType
from anypathlib.path_handlers.azure_handler import AzureHandler
from anypathlib.path_handlers.local_handler import LocalPathHandler
from anypathlib.path_handlers.s3_handler import S3Handler

PATH_TYPE_TO_BASE_TEST_PATH = {PathType.s3: r'',
                               PathType.azure: r'',
                               PathType.local: r'/tmp/AnyPath/tests/'}
PATH_TYPE_TO_HANDLER = {PathType.s3: S3Handler, PathType.azure: AzureHandler, PathType.local: LocalPathHandler}
