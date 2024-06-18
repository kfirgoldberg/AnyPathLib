import pytest

from anypathlib import PathType, AnyPath
from tests.tests_urls import PATH_TYPE_TO_HANDLER
from fixtures_anypath import temp_local_dir, temp_dir_with_files, clean_remote_dir


@pytest.mark.usefixtures("temp_dir_with_files", "temp_local_dir", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.azure, PathType.s3, PathType.local])
def test_copy_file_to_dir(path_type: PathType, temp_dir_with_files, temp_local_dir, clean_remote_dir):
    path_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_dir_files = temp_dir_with_files

    remote_dir = clean_remote_dir
    path_handler.upload_directory(local_dir=local_dir_path, target_url=remote_dir, verbose=False)
    source_files = AnyPath(remote_dir).iterdir()
    remote_file = source_files[0]
    local_downloaded_file_path = AnyPath(remote_file).copy(target=temp_local_dir, force_overwrite=True)
    assert local_downloaded_file_path.exists()
    assert local_downloaded_file_path.name == remote_file.name
    assert local_downloaded_file_path.is_file()
    assert local_downloaded_file_path.parent.base_path == AnyPath(temp_local_dir).base_path
