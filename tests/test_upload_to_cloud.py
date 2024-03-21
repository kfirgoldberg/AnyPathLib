import pytest

from anypathlib import PathType, AnyPath
from tests.tests_urls import PATH_TYPE_TO_HANDLER
from fixtures_anypath import temp_local_dir, temp_dir_with_files, clean_remote_dir


@pytest.mark.usefixtures("temp_dir_with_files", "temp_local_dir", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3])
def test_copy_from_local_to_cloud(path_type: PathType, temp_dir_with_files, temp_local_dir, clean_remote_dir):
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_dir_files = temp_dir_with_files
    remote_dir = clean_remote_dir
    local_anypath = AnyPath(local_dir_path)
    local_anypath.copy(target=AnyPath(remote_dir))
    remote_dir_files = cloud_handler.listdir(remote_dir)
    cloud_handler.remove(remote_dir)
    assert sorted([remote_file.split('/')[-1] for remote_file in remote_dir_files]) == sorted(
        [local_dir_file.name for local_dir_file in local_dir_files])
