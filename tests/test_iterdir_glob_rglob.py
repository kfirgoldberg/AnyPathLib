import pytest
from anypathlib import PathType, AnyPath
from tests.tests_urls import PATH_TYPE_TO_HANDLER
from fixtures_anypath import temp_dir_with_files, clean_remote_dir, temp_nested_dir


@pytest.mark.usefixtures("temp_nested_dir", "clean_remote_dir")
@pytest.mark.parametrize("path_type", [PathType.local, PathType.azure, PathType.s3])
def test_rglob_glob_iterdir(path_type: PathType, temp_nested_dir, clean_remote_dir):
    # TODO: add dirs to returned values in s3, azure
    cloud_handler = PATH_TYPE_TO_HANDLER[path_type]
    local_dir_path, local_files_top_level, local_nested_files = temp_nested_dir
    all_local_files = local_files_top_level + local_nested_files
    remote_dir = clean_remote_dir
    cloud_handler.upload_directory(local_dir=local_dir_path, target_url=remote_dir, verbose=False)
    remote_all_files = AnyPath(remote_dir).rglob(pattern='*')
    assert sorted([fn.name for fn in remote_all_files]) == sorted([fn.name for fn in all_local_files])
    remote_files_top_level_glob = AnyPath(remote_dir).glob(pattern='*')
    assert sorted([fn.name for fn in remote_files_top_level_glob]) == sorted([fn.name for fn in local_files_top_level])
    remote_files_top_level_iterdir = AnyPath(remote_dir).iterdir()
    assert sorted([fn.name for fn in remote_files_top_level_iterdir]) == sorted(
        [fn.name for fn in local_files_top_level])
