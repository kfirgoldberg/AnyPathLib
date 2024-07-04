import pytest

from anypathlib import PathType, AnyPath
from tests.tests_urls import PATH_TYPE_TO_HANDLER


@pytest.mark.usefixtures("temp_dir_with_files", "temp_local_dir", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3])
def test_copy_to_local_from_cloud(path_type: PathType, temp_dir_with_files, temp_local_dir, clean_remote_dir):
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_dir_files = temp_dir_with_files

    remote_dir = clean_remote_dir
    cloud_handler.upload_directory(local_dir=local_dir_path, target_url=remote_dir, verbose=False)
    local_download_dir = AnyPath(remote_dir).copy(target=AnyPath(temp_local_dir), force_overwrite=True)
    remote_files = AnyPath(remote_dir).rglob('*')
    assert sorted([fn.name for fn in remote_files]) == sorted(
        [fn.name for fn in local_download_dir.rglob('*')])
